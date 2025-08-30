import xml.etree.ElementTree as ET

import requests
from flask import Flask, render_template, request

app = Flask(__name__, template_folder=".")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        query_raw = request.form["query"]
        clean_query = query_raw.replace("-", "").replace("_", "")

        api_url = None
        error_message = None
        if clean_query.isdigit():
            if len(clean_query) == 10 or len(clean_query) == 13:
                api_url = f"https://ndlsearch.ndl.go.jp/api/opensearch?isbn={clean_query}&cnt=20"
            else:
                error_message = "ISBNは10桁または13桁の数字でなければなりません。"
        else:
            error_message = "ISBNは数字のみで構成されている必要があります（ハイフンやアンダースコアは含めません）。"
        if error_message:
            return render_template("1756479630.html", show_form=True, error=error_message, query=query_raw)

        all_results = []
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
                publication_place = publication_place_element.text if publication_place_element is not None else "不明"
                price = price_element.text if price_element is not None else "不明"
                pages = extent_element.text if extent_element is not None else "不明"
                subjects_str = ", ".join(subjects) if subjects else "不明"

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
                }
                if book_data not in all_results:
                    all_results.append(book_data)

        except requests.exceptions.RequestException as e:
            error_message = f"APIリクエスト中にエラーが発生しました: {e}"
        except ET.ParseError as e:
            error_message = f"XMLデータのパース中にエラーが発生しました: {e}"
        except Exception as e:
            error_message = f"予期せぬエラーが発生しました: {e}"

        if error_message:
            return render_template("1756479630.html", show_form=True, error=error_message, query=query_raw)
        else:
            return render_template("1756479630.html", show_results=True, results=all_results, query=query_raw)
    else:
        return render_template("1756479630.html", show_form=True)


if __name__ == "__main__":
    from waitress import serve

    serve(app, host="127.0.0.1", port=8080)
