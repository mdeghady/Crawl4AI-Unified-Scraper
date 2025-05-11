from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

import re

class FallbackJsonCssExtractionStrategy(JsonCssExtractionStrategy):
    def _extract_single_field(self, element, field):
      if "selector" in field:
        if isinstance(field["selector"], list) and len(field["selector"]) > 0:
          for field_selector in field["selector"]:
            selected = self._get_elements(element, field_selector)
            if selected:
              break
        else:
            selected = self._get_elements(element, field["selector"])
        if not selected:
            return field.get("default")
        selected = selected[0]
      else:
          selected = element

      value = None
      if field["type"] == "text":
          value = self._get_element_text(selected)
      elif field["type"] == "attribute":
          value = self._get_element_attribute(selected, field["attribute"])
      elif field["type"] == "html":
          value = self._get_element_html(selected)
      elif field["type"] == "regex":
          text = self._get_element_text(selected)
          match = re.search(field["pattern"], text)
          value = match.group(1) if match else None

      if "transform" in field:
          value = self._apply_transform(value, field["transform"])

      return value if value is not None else field.get("default")