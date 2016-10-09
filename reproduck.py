import json
import copy
from selenium import webdriver
from PIL import Image


class Element:

    def __init__(self, tag_name, attributes, content):
        self.tag_name = tag_name
        self.attributes = attributes
        self.content = content
        self.style = {}

    def __str__(self):
        return self.to_html()

    def multiply_by_styles(self, props):
        elements = [self]

        for prop in props:
            new_elements = []
            for e in elements:
                new_elements = new_elements + e.multiply_by_style_prop(prop)
            elements = new_elements

        return elements

    def multiply_by_style_prop(self, prop):
        elements = []
        n = round((prop['max'] - prop['min']) / prop['increment'])

        for i in range(n):
            prop_value = prop['min'] + i * prop['increment']
            prop_value_string = str(prop_value) + prop['measure_unit']

            element = copy.deepcopy(self)
            element.add_style_property(prop['name'], prop_value_string)
            elements.append(element)

        return elements

    def add_style_property(self, name, value):
        self.style[name] = value

    def to_html(self):
        styles = [k + ': ' + self.style[k] for k in self.style.keys()]
        style = '; '.join(styles)
        attributes = self.attributes + ' ' + 'style="' + style + '"'
        opening_tag = '<' + self.tag_name + ' ' + attributes + '>'
        closing_tag = '</' + self.tag_name + '>'

        return opening_tag + self.content + closing_tag


def generate_html(elements):
    return '''<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Document</title>
        </head>
        <body>
            %s
        </body>
        </html>''' % ''.join(elements)


def getElementImage(element, screenshot):
    location = element.location
    size = element.size

    left = location['x']
    top = location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']

    return screenshot.crop((left, top, right, bottom))
    return 'a'


def generateImages(config):
    base_element = Element(tag_name=config['tag_name'],
                           attributes=config['attributes'],
                           content=config['content'])

    styled_elements = base_element.multiply_by_styles(config['styles'])
    string_elements = [e.to_html() for e in styled_elements]
    html = generate_html(string_elements)

    with open(config['html_output'], "w") as html_file:
        html_file.write(html)

    # driver = webdriver.Chrome(config['webdriver_path'])
    driver = webdriver.PhantomJS()
    driver.get(config['html_path'])
    driver.save_screenshot('screenshot.png')
    elements = driver.find_elements_by_tag_name(config['tag_name'])

    screenshot = Image.open('screenshot.png')

    for i, element in enumerate(elements):
        image = getElementImage(element, screenshot)
        image.save('image_%s.png' % (i))

    driver.quit()


def main():
    with open('config.json') as config_file:
        config = json.load(config_file)
    generateImages(config)


if __name__ == '__main__':
    main()
