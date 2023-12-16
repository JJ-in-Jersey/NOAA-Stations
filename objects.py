from pathlib import Path


class CurrentWaypoint:
    xml = '<?xml version="1.1"?>'
    openGPX = '<gpx version="1.1" xmlns="http://www.topografix.com/GPX/1/1" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/GpxExtensions/v3 http://www8.garmin.com/xmlschemas/GpxExtensionsv3.xsd">'
    # symbol = 'Symbol-Spot-Orange'
    endWPT = '</wpt>'
    endGPX = '</gpx>'
    hrefBase = 'https://tidesandcurrents.noaa.gov/noaacurrents/'

    def __init__(self, tag):
        self.url = self.hrefBase + tag['href']
        self.lat = round(float(tag['onmouseover'].split(' ')[1].split(',')[0]), 4)
        self.lon = -1*round(float(tag['onmouseover'].split(' ')[1].split(',')[1][:-2]), 4)
        self.name = tag.text
        self.mapName = tag['href'].split('=')[1]
        self.type = tag.find_parent('tr').find_all()[-1].text
        if self.type == 'Harmonic':
            self.symbol = 'Symbol-Spot-Orange'
        elif self.type == 'Subordinate':
            self.symbol = 'Symbol-Circle-Orange'

    def write_me(self, output_dir):
        nl = '\n'
        filename = self.mapName + '.gpx'
        filepath = Path(str(output_dir) + '/' + filename)
        file = open(filepath, "w")
        file.write(f'{self.xml}{nl}')
        file.write(f'{self.openGPX}{nl}')
        file.write(f'  <wpt lat="{self.lat}" lon="{self.lon}">{nl}')
        file.write(f'    <name>{self.name + ' cs'}</name>{nl}')
        file.write(f'    <sym>{self.symbol}</sym>{nl}')
        file.write(f'    <type>{self.type}</type>{nl}')
        file.write(f'    <link href="{self.url}">{nl}')
        file.write(f'      <text>{self.mapName} {self.lat} {self.lon}</text>{nl}')
        file.write(f'    </link>{nl}')
        file.write(f'  {self.endWPT}{nl}')
        file.write(f'{self.endGPX}{nl}')
        file.close()


class TideWaypoint:
    xml = '<?xml version="1.1"?>'
    openGPX = '<gpx version="1.1" xmlns="http://www.topografix.com/GPX/1/1" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/GpxExtensions/v3 http://www8.garmin.com/xmlschemas/GpxExtensionsv3.xsd">'
    # symbol = 'Symbol-Spot-Yellow'
    endWPT = '</wpt>'
    endGPX = '</gpx>'
    hrefBase = 'https://tidesandcurrents.noaa.gov/noaatidepredictions.html?id='

    def __init__(self, row):
        # row [name, code, lat, lon, type]
        self.name = row[0]
        self.code = row[1]
        self.lat = float(row[2])
        self.lon = float(row[3])
        self.type = row[4]
        self.url = self.hrefBase + row[1]
        if self.type == 'Harmonic':
            self.symbol = 'Symbol-Spot-Yellow'
        elif self.type == 'Subordinate':
            self.symbol = 'Symbol-Circle-Yellow'

    def write_me(self, output_dir):
        nl = '\n'
        filename = self.code + '.gpx'
        filepath = Path(str(output_dir) + '/' + filename)
        file = open(filepath, "w")
        file.write(f'{self.xml}{nl}')
        file.write(f'{self.openGPX}{nl}')
        file.write(f'  <wpt lat="{self.lat}" lon="{self.lon}">{nl}')
        file.write(f'    <name>{self.name + ' ts'}</name>{nl}')
        file.write(f'    <sym>{self.symbol}</sym>{nl}')
        file.write(f'    <type>{self.type}</type>{nl}')
        file.write(f'    <link href="{self.url}">{nl}')
        file.write(f'      <text>{self.code} {self.lat} {self.lon}</text>{nl}')
        file.write(f'    </link>{nl}')
        file.write(f'  {self.endWPT}{nl}')
        file.write(f'{self.endGPX}{nl}')
        file.close()
