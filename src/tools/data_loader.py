import asyncio
import datetime
import json
import os
import sys

import progressbar
from dateutil.parser import parse
from sqlalchemy import Insert, func, select

from src.models.model import maintainer, package, release, user
from src.utils.cookie_auth import try_int
from src.utils.security import hash_password

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.database import execute, fetch_all, fetch_scalar


async def main():
    select_query = select(func.count()).select_from(user)
    user_count = await fetch_scalar(select_query)

    if user_count == 0:
        file_data = do_load_files()
        users = find_users(file_data)
        db_users = await do_user_import(users)
        await do_import_packages(file_data, db_users)

    await do_summary()


async def do_summary():
    print("Final numbers:")
    print("Users: {}".format(await fetch_scalar(select(func.count(user.c.id)))))
    print("Packages: {}".format(await fetch_scalar(select(func.count(package.c.id)))))
    print("Releases: {}".format(await fetch_scalar(select(func.count(release.c.id)))))
    print(
        "Maintainers: {}".format(
            await fetch_scalar(select(func.count(maintainer.c.id)))
        )
    )


async def do_user_import(user_lookup: dict[str, str]) -> dict[str, user]:
    users = []
    print("Importing users ... ", flush=True)
    with progressbar.ProgressBar(max_val=len(user_lookup)) as bar:
        for idx, (email, name) in enumerate(user_lookup.items()):
            users.append(
                {
                    "email": email,
                    "name": name,
                    "hash_password": hash_password("123456"),
                }
            )
            bar.update(idx)
    insert_query = Insert(user).values(users).returning(user)
    await fetch_all(insert_query)

    select_email = select(user).filter(user.c.email.isnot(None))
    return {u.get("email"): u for u in await fetch_all(select_email)}


async def do_import_packages(file_data: list[dict], user_lookup: dict[str, user]):
    error_packages = []
    print("Importing packages and releases ... ", flush=True)
    with progressbar.ProgressBar(max_value=len(file_data)) as bar:
        for idx, p in enumerate(file_data):
            try:
                await load_package(p, user_lookup)
                bar.update(idx)
            except Exception as x:
                error_packages.append(
                    (
                        p,
                        " *** Errored out for package {}, {}".format(
                            p.get("package_name"), x
                        ),
                    )
                )
                raise
    print("Completed packages with {} errors.".format(len(error_packages)))
    for p, txt in error_packages:
        print(txt)


def do_load_files() -> list[dict]:
    data_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../data/pypi-top-100")
    )
    print("Loading files from {}".format(data_path))
    files = get_file_names(data_path)
    print("Found {:,} files, loading ...".format(len(files)), flush=True)
    return [load_file_data(f) for f in files]


def find_users(data: list[dict]) -> dict:
    print("Discovering users...", flush=True)
    found_users = {}

    for idx, p in enumerate(data):
        info = p.get("info")
        found_users.update(
            get_email_and_name_from_text(info.get("author"), info.get("author_email"))
        )
        found_users.update(
            get_email_and_name_from_text(
                info.get("maintainer"), info.get("maintainer_email")
            )
        )
    print("Discovered {:,} users".format(len(found_users)))
    return found_users


def get_email_and_name_from_text(name: str, email: str) -> dict:
    data = {}

    if not name:
        return data

    if not email:
        email = ""

    emails = email.strip().lower().split(",")
    names = name
    if len(email) > 1:
        names = name.strip().split(",")

    for n, e in zip(names, emails, strict=False):
        if not n or not e:
            continue

        data[e.strip()] = n.strip()

    return data


def load_file_data(filename: str) -> dict:
    try:
        with open(filename, "r", encoding="utf-8") as fin:
            data = json.load(fin)
    except Exception as x:
        print("ERROR in file: {}, details: {}".format(filename, x), flush=True)
        raise

    return data


async def load_package(data: dict, user_lookup: dict[str, user]):
    try:
        info = data.get("info", {})
        releases = build_releases(
            data.get("package_name", "").strip(), data.get("releases", {})
        )
        if not (created_date := releases[0].get("created_date")):
            created_date = datetime.datetime.now()

        maintainers_lookup = get_email_and_name_from_text(
            info.get("maintainer"), info.get("maintainer_email")
        )

        insert_query = (
            Insert(package)
            .values(
                {
                    "id": data.get("package_name", "").strip(),
                    "create_at": created_date,
                    "author_name": info.get("author"),
                    "author_email": info.get("author_email"),
                    "summary": info.get("summary"),
                    "description": info.get("description"),
                    "home_page": info.get("home_page"),
                    "docs_url": info.get("docs_url"),
                    "package_url": info.get("package_url"),
                    "license": detect_license(info.get("license")),
                },
            )
            .returning(package)
        )

        await execute(insert_query)
        insert_release = Insert(release).values(releases).returning(release)
        await execute(insert_release)
        if maintainers_lookup:
            insert_maintainer = Insert(maintainer).values(
                {
                    "maintainer": list(maintainers_lookup.values())[0],
                    "maintainer_email": list(maintainers_lookup.keys())[0],
                    "profile_image_url": info.get("profile_image_url"),
                    "package_id": data.get("package_name", "").strip(),
                },
            )
            await execute(insert_maintainer)
    except OverflowError:
        # What the heck, people just putting fake data in here
        # Size is terabytes...
        pass
    except Exception:
        raise


def detect_license(license_text: str) -> str | None:
    if not license_text:
        return None

    license_text = license_text.strip()

    if len(license_text) > 100 or "\n" in license_text:
        return "CUSTOM"

    license_text = license_text.replace("Software License", "").replace("License", "")

    if "::" in license_text:
        # E.g. 'License :: OSI Approved :: Apache Software License'
        return license_text.split(":")[-1].replace("  ", " ").strip()

    return license_text.strip()


def build_releases(package_id: str, releases: dict) -> list[release]:
    db_releases = []
    for k in releases.keys():
        all_releases_for_version = releases.get(k)
        if not all_releases_for_version:
            continue

        v = all_releases_for_version[-1]
        major_ver, minor_ver, build_ver = make_version_num(k)

        db_releases.append(
            {
                "package_id": package_id,
                "major_ver": major_ver,
                "minor_ver": minor_ver,
                "build_ver": build_ver,
                "create_at": parse(v.get("upload_time")),
                "comment": v.get("comment_text"),
                "url": v.get("url"),
                "size": int(v.get("size", 0)),
            },
        )

    return db_releases


def make_version_num(version_text):
    major, minor, build = 0, 0, 0
    if version_text:
        version_text = version_text.split("b")[0]
        parts = version_text.split(".")
        if len(parts) == 1:
            major = try_int(parts[0])
        elif len(parts) == 2:
            major = try_int(parts[0])
            minor = try_int(parts[1])
        elif len(parts) == 3:
            major = try_int(parts[0])
            minor = try_int(parts[1])
            build = try_int(parts[2])

        return major, minor, build


def get_file_names(data_path: str) -> list[str]:
    files = []
    for f in os.listdir(data_path):
        if f.endswith(".json"):
            files.append(os.path.abspath(os.path.join(data_path, f)))

    files.sort()
    return files


if __name__ == "__main__":
    asyncio.run(main())
