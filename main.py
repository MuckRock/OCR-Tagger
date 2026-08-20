"""
Simple DocumentCloud Add-On that tags documents
with the OCR engine used on said documents.
"""

import sys
import time

import requests
from documentcloud.addon import AddOn
from documentcloud.exceptions import APIError


class OCRTagger(AddOn):
    """Tags documents with OCR engine"""

    def tag_document(self, document, value, max_retries=5, retry_delay=60):
        """Tags document with OCR engine"""
        retries = 0
        while retries < max_retries:
            try:
                print("Tagging document...")
                self.client.patch(
                    f"documents/{document.id}/",
                    json={"data": {"ocr_engine": value}},
                )
                print("Finished tagging document")
                break
            except APIError as exc:
                print(f"Error tagging document. {exc}. Retrying...")
                retries += 1
                time.sleep(retry_delay)
        else:
            print(f"Failed to tag document after {max_retries} attempts.")
            self.set_message(
                "Failed to set the OCR tag for this document. "
                "Email info@documentcloud.org to debug."
            )
            sys.exit(1)

    def main(self):
        """For each document finds the ocr value from the json text and tags"""

        self.client.session.headers.update({"User-Agent": "OCR Tagger Add-On"})
        for document in self.get_documents():
            try:
                json_text_url = f"""
                    {document.asset_url}documents/
                    {document.id}/{document.slug}.txt.json
                """
                response = requests.get(json_text_url, timeout=10)
                json_data = response.json()
                ocr_value = json_data["pages"][0]["ocr"]
            except requests.exceptions.RequestException:
                ocr_value = "None"
            ocr_mapping = {
                "tess4": "tesseract",
                "tess4_force": "tesseract",
                "textract": "textract",
                "textract_force": "textract",
                "azuredi": "azure",
                "googlecv": "google",
                "doctr": "doctr",
                "None": "None",
            }

            ocr_value_to_tag = ocr_mapping.get(ocr_value)

            self.tag_document(document, ocr_value_to_tag)


if __name__ == "__main__":
    OCRTagger().main()
