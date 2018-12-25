import json

from datetime import datetime
from lxml import etree

xml_return = 'RS_Via-3.xml'
xml_oneway = 'RS_ViaOW.xml'


def display(xml):
    """Create json to display"""
    results = parse(xml)
    for i in results:
        delta = convert_timedelta(i['duration'])
        i['duration'] = delta
    return json.dumps(results)


def parse(xml):
    """Parse the XML file"""
    with open(xml) as f:
        tree = etree.parse(f)

    root = tree.getroot()
    results = list()

    for flight_data in root.findall('.//PricedItineraries/Flights'):

        # Make clear whether we have one_way or return flight
        query_type = 'return'
        g = flight_data.xpath('.//ReturnPricedItinerary')
        if not flight_data.xpath('.//ReturnPricedItinerary'):
            query_type = 'one_way'

        quote = dict()
        quote['flight_type'] = query_type
        currency = {'currency': flight_data.xpath('.//Pricing/@currency')[0]}
        adult_fare = {
            'adult': flight_data.xpath(
                './/Pricing/ServiceCharges[@type="SingleAdult"][@ChargeType="TotalAmount"]/text()')[0]}
        fare_basis = [currency, adult_fare]
        if query_type == 'one_way':
            child_fare = {
                'child': flight_data.xpath(
                    './/Pricing/ServiceCharges[@type="SingleChild"][@ChargeType="TotalAmount"]/text()')[0]}
            infant_fare = {
                'infant': flight_data.xpath(
                    './/Pricing/ServiceCharges[@type="SingleInfant"][@ChargeType="TotalAmount"]/text()')[0]}
            fare_basis.extend([child_fare, infant_fare])

        # Adding fare basis to the quote
        quote['farebasis'] = fare_basis

        segments = list()

        for flight in flight_data:
            leg = get_leg(flight.tag)
            if leg is not None:
                for seg in flight.findall('.//Flights/Flight'):
                    segment = make_segment(seg, leg)
                    segments.append(segment)
            quote['duration'] = get_flight_length(segments)
            quote['segments'] = segments
        results.append(quote)

    return results


def get_flight_length(segments):
    dep_date = datetime.strptime(segments[0]['departure_time'], '%Y-%m-%dT%H%M')
    arr_date = datetime.strptime(segments[-1]['arrival_time'], '%Y-%m-%dT%H%M')
    # arr_date = datetime.strptime('2018-10-28T0850', '%Y-%m-%dT%H%M') # for debug purposes
    delta = arr_date - dep_date
    return delta


def get_leg(tag):
    """Get the number of legs: 0 for outbound flights, 1 for inbound"""
    leg = None
    if tag == 'OnwardPricedItinerary':
        leg = 0
    if tag == 'ReturnPricedItinerary':
        leg = 1
    return leg


def make_segment(flight, leg):
    """Creating flight segment"""
    segment = dict()
    segment['carrier'] = flight.xpath('.//Carrier/text()')[0]
    segment['flight_number'] = flight.xpath('.//Carrier/@id')[0] + flight.xpath('.//FlightNumber/text()')[0]
    segment['departure_iata'] = flight.xpath('.//Source/text()')[0]
    segment['arrival_iata'] = flight.xpath('.//Destination/text()')[0]
    segment['departure_time'] = flight.xpath('.//DepartureTimeStamp/text()')[0]
    segment['arrival_time'] = flight.xpath('.//ArrivalTimeStamp/text()')[0]
    segment['category'] = flight.xpath('.//Class/text()')[0]
    segment['ticket_type'] = flight.xpath('.//TicketType/text()')[0]
    segment['leg'] = leg
    return segment


def convert_timedelta(duration):
    """Convert timedelta to hours and minutes for serialization means"""
    days, seconds = duration.days, duration.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    return {
        'hours': hours,
        'minutes': minutes
    }


if __name__ == '__main__':
    display(xml_oneway)
