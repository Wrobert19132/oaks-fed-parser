import pypdf
import re
import datetime
import subprocess
import pdfplumber
import pathlib


START_PAGE = 2
OUTPUT_DIR = pathlib.Path.cwd() / "output"
INPUT_NAME = "input.pdf"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def create_image(title, data, caption, date: datetime.datetime):
    title = OUTPUT_DIR / title

    with open(title, "wb") as file:
        file.write(data)

    subprocess.run([
        "exiftool",
        "-overwrite_original",
        f'-iptc:Caption-Abstract={caption}',
        f'{title.as_posix()}'
    ])

    cmd = [
        "touch",
        "-c",
        "-t",
        f"{date.strftime('%Y%m%d%H%M')}",
        f'{title.as_posix()}'
    ]

    subprocess.run(cmd)


class Entry:
    def __init__(self):
        self.entry_name = None
        self.note = None
        self.author = None
        self.taken = None
        self.pictures = {}

    def __repr__(self):
        return f"<Entry: {self.entry_name} - {self.author}, {len(self.pictures)} pictures>"

    def add_picture(self, name, picture):
        self.pictures[name] = picture

    def caption(self):
        return f"{self.entry_name}: {self.note}"

    def set_name(self, name):
        self.entry_name = name

    def set_author(self, name):
        self.author = name

    def set_note(self, note: str):
        self.note = note

    def set_datetime(self, date: datetime.datetime):
        self.taken = date

    def valid(self):
        for attribute in (self.entry_name, self.author, self.taken, self.note):
            if attribute is None:
                return False
        if len(self.pictures) == 0:
            return False

        return True


def main(input_name, start_page):
    reader = pypdf.PdfReader(input_name)
    plumber_reader = pdfplumber.open(input_name)

    entry = Entry()

    for page, plumberPage in zip(reader.pages[start_page:], plumber_reader.pages[start_page:]):
        page: pypdf.PageObject
        plumberPage: pdfplumber.page.Page

        text = plumberPage.extract_text()
        lines = text.split("\n")[1:]

        if "Notes" in lines:
            note = " ".join(lines[lines.index("Notes") + 1:-1])
            entry.set_note(note)
        if lines[0] != "Notes":
            entry.set_name(lines[0])

        for image_file_object in page.images[1:]:
            entry.add_picture(image_file_object.name, image_file_object)

        author = re.search("By (.*) -.*", text, re.MULTILINE)
        if author:
            entry.set_author(author.group(1))

        time = re.search("- Added (.. ... .... ..:.. ..)", text, re.MULTILINE)
        if time:
            entry.set_datetime(datetime.datetime.strptime(time.group(1), "%d %b %Y %I:%M %p"))

        if entry.valid():
            for name, image in entry.pictures.items():
                path = pathlib.Path(".") / "output"
                path.mkdir(parents=True, exist_ok=True)
                with open(path / f"{entry.entry_name} - {image.name}", "wb") as fp:
                    fp.write(image.data)

            print(entry)
            print(entry.note)
            print(entry.author)

            for picture_name, picture in entry.pictures.items():
                create_image(f"{entry.entry_name} - {picture_name}",
                             picture.data,
                             f"{entry.entry_name}: {entry.note} -{entry.author}",
                             entry.taken
                             )
            entry = Entry()


if __name__ == "__main__":
    main(INPUT_NAME, START_PAGE)
