import sys

from datetime import datetime
from lxml import etree


def parse(xml):
    """
    Calls main parsing function.
    Argument:
        - XML filename in string format, ex. 'RS_ViaOW.xml'.
    Returns parsed results (list of quotes) in case of success,
    prints out error message in case of error.
    """

    try:
        quotes = parse_file(xml)
        return quotes

    except Exception as e:
        print('Failed to parse XML: {}'.format(e), file=sys.stderr)
        return 'Sorry, the service is currently unavailable. :( Please try again later.'


def parse_file(xml):
    """
    Parses the XML file with flights.
        - Argument: XML filename in string format, ex. 'RS_ViaOW.xml'.
    Returns a list with quotes - flights results in dictionaries.
    """
    with open(xml) as f:
        tree = etree.parse(f)

    root = tree.getroot()
    results = list()

    for flight_data in root.findall('.//PricedItineraries/Flights'):

        # Make clear whether we have one_way or return flight.
        query_type = 'return'
        if not flight_data.xpath('.//ReturnPricedItinerary'):
            query_type = 'one_way'

        # Create a quote: a valid result.
        quote = dict()
        quote['flight_type'] = query_type

        # Add fare basis to the quote
        fares = get_fares(query_type, flight_data)
        quote['farebasis'] = fares

        # Create segments - a list of all flights including stops.
        segments = list()

        # A flight leg is a flight from 'A' to 'B' that can have a stop in 'C'.
        # A leg equals to 0 for outbound flights, to 1 for inbound flights, 2 and more for multidestination.
        for leg, flight in enumerate(flight_data):
            if flight.tag == 'Pricing':
                break
            else:
                for seg in flight.findall('.//Flights/Flight'):
                    segment = make_segment(seg, leg)
                    segments.append(segment)
            quote['duration_' + str(leg)] = get_flight_length(segments, leg)
            quote['segments'] = segments
        results.append(quote)

    return results


def get_fares(query_type, flight_data):
    """
    Parses fares and fills fares list.
    Arguments:
        - query_type: 'one_way' or 'return';
        - flight_data: XML Element 'Flights'.
    Returns a list of fares with currency and fare_type.
    """

    currency = {'currency': flight_data.xpath('.//Pricing/@currency')[0]}
    adult_fare = {
        'adult': flight_data.xpath(
            './/Pricing/ServiceCharges[@type="SingleAdult"][@ChargeType="TotalAmount"]/text()')[0]
    }

    # Return flights have fare for adult only, meaning a child fare equals adult fare and infant is free.
    child_fare = {
        'child': flight_data.xpath(
            './/Pricing/ServiceCharges[@type="SingleChild"][@ChargeType="TotalAmount"]/text()')[0]
    } if query_type == 'one_way' else {
        'child': flight_data.xpath(
            './/Pricing/ServiceCharges[@type="SingleAdult"][@ChargeType="TotalAmount"]/text()')[0]
    }
    infant_fare = {
        'infant': flight_data.xpath(
            './/Pricing/ServiceCharges[@type="SingleInfant"][@ChargeType="TotalAmount"]/text()')[0]
    } if query_type == 'one_way' else {'infant': 0}
    fare_type = {
        'fare_type': 'age_dependant'
    } if query_type == 'one_way' else {'fare_type': 'fixed_fare'}

    return [currency, adult_fare, child_fare, infant_fare, fare_type]


def make_segment(flight, leg):
    """
    Creates flight segment dictionary. A 'leg' 'DXB - BKK' can have two segments: 'DXB - DEL', 'DEL - BKK'.
    Arguments:
        - flight: XML Element 'Flight';
        - leg: int value: 0 for an outbound flight, 1 for inbound, 2 and more for multidestination.
    Returns one flight segment as a dictionary.
    """
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


def get_flight_length(segments, leg):
    """
    Gets duration of each segment.
    Arguments:
        - segments: list of flight segments;
        - leg: int value: 0 for an outbound flight, 1 for inbound, 2 and more for multidestination.
    Returns duration of a leg (flight with stops) as a dictionary.
    """
    segments = [x for x in segments if x['leg'] == leg]
    dep_date = datetime.strptime(segments[0]['departure_time'], '%Y-%m-%dT%H%M')
    arr_date = datetime.strptime(segments[-1]['arrival_time'], '%Y-%m-%dT%H%M')

    return convert_timedelta(arr_date - dep_date)


def convert_timedelta(duration):
    """
    Converts timedelta to a dictionary with hours and minutes for serialization means.
    Argument:
        - duration: timedelta object.
    """
    days, seconds = duration.days, duration.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60

    return {
        'hours': hours,
        'minutes': minutes,
        'total minutes': hours * 60 + minutes
    }
