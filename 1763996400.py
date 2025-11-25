import json
import os
import xml.etree.ElementTree as ET

import requests
from flask import Flask, redirect, render_template, request, url_for

BOOKSHELF_FILE = "bookshelf.json"
STATUS_MAP = {
    "unread": "未読",
    "reading": "読書中",
    "read": "既読",
}
STATUS_OPTIONS = list(STATUS_MAP.keys())


def load_books_data():
    """Load book data from the JSON file."""
    if not os.path.exists(BOOKSHELF_FILE):
        return {}
    try:
        with open(BOOKSHELF_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_books_data(data):
    """Save book data to the JSON file."""
    try:
        with open(BOOKSHELF_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"ERROR: Failed to save book data: {e}")


app = Flask(__name__, template_folder=".")


@app.route("/", methods=["GET", "POST"])
def index():
    books_data = load_books_data()
    error_message = None
    query_raw = ""
    all_results = []

    if request.method == "POST":
        action = request.form.get("action")

        if action == "update_status":
            isbn_key = request.form.get("isbn_key")
            new_status = request.form.get("new_status")

            if isbn_key and new_status in STATUS_OPTIONS:
                if isbn_key in books_data:
                    books_data[isbn_key]["status"] = new_status
                    save_books_data(books_data)
                    return redirect(url_for("index"))

                else:
                    book_details = {
                        k: request.form.get(k)
                        for k in [
                            "title",
                            "creator",
                            "title_transcription",
                            "creator_transcription",
                            "publisher",
                            "publication_date",
                            "publication_place",
                            "price",
                            "pages",
                            "subjects",
                            "isbn10",
                            "isbn13",
                        ]
                    }
                    book_details = {k: v for k, v in book_details.items() if v is not None}

                    if book_details.get("title"):
                        book_details["status"] = new_status
                        books_data[isbn_key] = book_details
                        save_books_data(books_data)
                        return redirect(url_for("index"))
                    else:
                        error_message = "書籍の追加に必要な情報が不足しています。"
            else:
                error_message = "無効な書籍情報またはステータスです。"

        elif action == "delete_book":
            isbn_key = request.form.get("isbn_key")
            if isbn_key and isbn_key in books_data:
                del books_data[isbn_key]
                save_books_data(books_data)
                return redirect(url_for("index"))
            else:
                error_message = "削除対象の書籍が見つかりませんでした。"

        elif request.form.get("query"):
            query_raw = request.form["query"]
            clean_query = query_raw.replace("-", "").replace("_", "")

            api_url = None
            if clean_query.isdigit():
                if len(clean_query) == 10 or len(clean_query) == 13:
                    api_url = f"https://ndlsearch.ndl.go.jp/api/opensearch?isbn={clean_query}&cnt=20"
                else:
                    error_message = "ISBNは10桁または13桁の数字でなければなりません。"
            else:
                error_message = "ISBNは数字のみで構成されている必要があります（ハイフンやアンダースコアは含めません）。"

            if api_url and not error_message:
                try:
                    response = requests.get(api_url)
                    response.raise_for_status()
                    root = ET.fromstring(response.content)
                    namespaces = {
                        "rss": "http://purl.org/rss/1.0/",
                        "dc": "http://purl.org/dc/elements/1.1/",
                        "dcndl": "http://ndl.go.jp/dcndl/terms/",
                    }

                    for item in root.findall(".//item", namespaces):
                        title_element = item.find("dc:title", namespaces)
                        creator_element = item.find("dc:creator", namespaces)
                        title_transcription_element = item.find("dcndl:titleTranscription", namespaces)
                        creator_transcription_element = item.find("dcndl:creatorTranscription", namespaces)
                        publisher_element = item.find("dc:publisher", namespaces)
                        date_element = item.find("dc:date", namespaces)
                        publication_place_element = item.find("dcndl:publicationPlace", namespaces)
                        price_element = item.find("dcndl:price", namespaces)
                        extent_element = item.find("dc:extent", namespaces)
                        subjects = [s.text for s in item.findall("dc:subject", namespaces) if s.text]
                        isbn10_found = None
                        isbn13_found = None

                        for identifier_element in item.findall("dc:identifier", namespaces):
                            xsi_type = identifier_element.get("{http://www.w3.org/2001/XMLSchema-instance}type")
                            if xsi_type == "dcndl:ISBN":
                                isbn_value_from_xml = identifier_element.text
                                if isbn_value_from_xml:
                                    cleaned_isbn_for_check = isbn_value_from_xml.replace("-", "")
                                    if len(cleaned_isbn_for_check) == 10 and not isbn10_found:
                                        isbn10_found = isbn_value_from_xml
                                    elif len(cleaned_isbn_for_check) == 13 and not isbn13_found:
                                        isbn13_found = isbn_value_from_xml

                        title = title_element.text if title_element is not None else "タイトル不明"
                        creator = creator_element.text if creator_element is not None else "著者不明"
                        title_transcription = (
                            title_transcription_element.text if title_transcription_element is not None else "不明"
                        )
                        creator_transcription = (
                            creator_transcription_element.text if creator_transcription_element is not None else "不明"
                        )
                        publisher = publisher_element.text if publisher_element is not None else "不明"
                        publication_date = date_element.text if date_element is not None else "不明"
                        publication_place = (
                            publication_place_element.text if publication_place_element is not None else "不明"
                        )
                        price = price_element.text if price_element is not None else "不明"
                        pages = extent_element.text if extent_element is not None else "不明"
                        subjects_str = ", ".join(subjects) if subjects else "不明"

                        isbn_key_raw = isbn13_found or isbn10_found
                        isbn_key = isbn_key_raw.replace("-", "") if isbn_key_raw else None

                        current_status = books_data.get(isbn_key, {}).get("status", "not_managed")

                        book_data = {
                            "title": title,
                            "creator": creator,
                            "title_transcription": title_transcription,
                            "creator_transcription": creator_transcription,
                            "publisher": publisher,
                            "publication_date": publication_date,
                            "publication_place": publication_place,
                            "price": price,
                            "pages": pages,
                            "subjects": subjects_str,
                            "isbn10": isbn10_found,
                            "isbn13": isbn13_found,
                            "isbn_key": isbn_key,
                            "current_status": current_status,
                            "status_display": STATUS_MAP.get(current_status, "未登録"),
                        }

                        if isbn_key and book_data not in all_results:
                            all_results.append(book_data)

                except requests.exceptions.RequestException as e:
                    error_message = f"APIリクエスト中にエラーが発生しました: {e}"
                except ET.ParseError as e:
                    error_message = f"XMLデータのパース中にエラーが発生しました: {e}"
                except Exception as e:
                    error_message = f"予期せぬエラーが発生しました: {e}"

    managed_books_by_status = {k: [] for k in STATUS_MAP.keys()}
    for isbn, book in books_data.items():
        status = book.get("status", "unread")

        book_display = book.copy()
        book_display["isbn_key"] = isbn
        book_display["status_key"] = status
        book_display["status_display"] = STATUS_MAP[status]

        if status in managed_books_by_status:
            managed_books_by_status[status].append(book_display)

    template_data = {
        "managed_books_by_status": managed_books_by_status,
        "status_map": STATUS_MAP,
        "status_options": STATUS_OPTIONS,
        "error": error_message,
    }

    if all_results:
        template_data["show_results"] = True
        template_data["results"] = all_results
        template_data["query"] = query_raw
    else:
        template_data["show_form"] = True
        if query_raw:
            template_data["query"] = query_raw

    return render_template("1763996430.html", **template_data)


@app.route("/books/<isbn>")
def book_details(isbn):
    books_data = load_books_data()
    book_data = books_data.get(isbn)

    if not book_data:
        return redirect(url_for("index"))

    current_status = book_data.get("status", "not_managed")

    detail_data = {
        "title": book_data.get("title", "タイトル不明"),
        "creator": book_data.get("creator", "著者不明"),
        "title_transcription": book_data.get("title_transcription", "不明"),
        "creator_transcription": book_data.get("creator_transcription", "不明"),
        "publisher": book_data.get("publisher", "不明"),
        "publication_date": book_data.get("publication_date", "不明"),
        "publication_place": book_data.get("publication_place", "不明"),
        "price": book_data.get("price", "不明"),
        "pages": book_data.get("pages", "不明"),
        "subjects": book_data.get("subjects", "不明"),
        "isbn10": book_data.get("isbn10"),
        "isbn13": book_data.get("isbn13"),
        "isbn_key": isbn,
        "current_status": current_status,
        "status_display": STATUS_MAP.get(current_status, "未登録"),
    }

    managed_books_by_status = {k: [] for k in STATUS_MAP.keys()}
    for k, book in books_data.items():
        status = book.get("status", "unread")
        book_display = book.copy()
        book_display["isbn_key"] = k
        book_display["status_key"] = status
        book_display["status_display"] = STATUS_MAP[status]
        if status in managed_books_by_status:
            managed_books_by_status[status].append(book_display)

    template_data = {
        "managed_books_by_status": managed_books_by_status,
        "status_map": STATUS_MAP,
        "status_options": STATUS_OPTIONS,
        "show_results": True,
        "results": [detail_data],
        "query": detail_data["title"],
        "error": None,
    }

    return render_template("1763996430.html", **template_data)


if __name__ == "__main__":
    from waitress import serve

    serve(app, host="127.0.0.1", port=8080)
