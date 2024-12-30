# """
# <?xml version='1.0' encoding='utf-8'?>
# <ns0:package xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:ns0="http://www.idpf.org/2007/opf" version="2.0">
# 	<ns0:metadata>
# 		<dc:title>Narrenturm</dc:title>
# 		<dc:creator ns0:role="aut">Andrzej Sapkowski</dc:creator>
# 		<dc:creator ns0:role="nrt">zespół lektorów</dc:creator>
# 		<dc:date />
# 		<dc:publisher />
# 		<dc:identifier opf:scheme="ISBN" />
# 		<dc:description>
# Świat nie zginął i nie spłonął. Przynajmniej nie cały.
# Ale i tak było wesoło.
# [...]
# Przed nami jeszcze dwa tomy trylogii. </dc:description>
# 		<dc:language>pol</dc:language>
# 		<ns0:meta name="calibre:series" content="Trylogia husycka" />
# 		<ns0:meta name="calibre:series_index" content="1" />
# 		<dc:subject>fantasy</dc:subject>
# 		<dc:subject>science fiction</dc:subject>
# 		<dc:tag>Nagroda Zajdla - zwycięzca</dc:tag>
# 		<dc:tag>Husyci</dc:tag>
# 		<dc:tag>Reynewen</dc:tag>
# 		<dc:tag>czarna magia</dc:tag>
# 		<dc:tag>biała magia</dc:tag>
# 		<dc:tag>Śląsk</dc:tag>
# 	</ns0:metadata>
# </ns0:package>
# """

def xml_element(name, value, prefix="dc:", postfix=""):
    return f"   <{prefix}{name}{postfix}>{value}</{prefix}{name}>\n"


def book_info_to_xml(book_info):
    xml = '<?xml version="1.0" encoding="utf-8"?>\
    <ns0:package xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:ns0="http://www.idpf.org/2007/opf" version="2.0">\
	<ns0:metadata>'

    for key in book_info:

        if "author" == key or "narrator" == key:
            continue

        xml_key = key
        prefix = "dc:"
        postfix = ""
        if "authors" in key:
            xml_key = "creator"
            postfix = ' opf:role="aut"'
        elif "narrator" in key:
            xml_key = "creator"
            postfix = ' opf:role="nrt"'
        elif "genres" in key:
            xml_key = "subject"
        elif "publishedDate" in key:
            xml_key = "date"
        elif "tags" == key:
            xml_key = "tag"
        elif "isbn" == key:
            xml_key = "identifier"
            postfix = ' opf:scheme="ISBN"'
        elif "id" == key:
            xml_key = "identifier"
            postfix = ' opf:scheme="ASIN"'
        elif "series" == key:
            xml_key = "meta"
            prefix = "ns0:"
            postfix = f' name="calibre:series" content="{book_info[key]}"'
        elif "series_num" == key:
            xml_key = "meta"
            prefix = "ns0:"
            postfix = f' name="calibre:series_index" content="{book_info[key]}"'

        if type(book_info[key]) == type([]):
            for value in book_info[key]:
                xml += xml_element(xml_key, value, prefix=prefix, postfix=postfix)
        else:
            xml += xml_element(xml_key, book_info[key], prefix=prefix, postfix=postfix)

    xml += "</ns0:metadata> </ns0:package>"

    return xml
