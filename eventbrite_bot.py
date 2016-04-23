import argparse
import cookielib
import urllib2
import zlib


class NoRedirection(urllib2.HTTPErrorProcessor):
    def http_response(self, request, response):
        return response

    https_response = http_response


class ArgHandler(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(ArgHandler, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        if option_string in ['-u', '--users']:
            setattr(namespace, 'users', values.readlines())
        if option_string in ['-i', '--eid']:
            setattr(namespace, 'eid', str(values))
        if option_string in ['-d', '--dump']:
            self.retrieve_ticket(namespace)

    def retrieve_ticket(self, namespace):
        # define base url
        url = 'https://www.eventbrite.com/event/' + namespace.eid
        # create opener
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(NoRedirection, urllib2.HTTPHandler(), urllib2.HTTPSHandler(),
                                      urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [
            ('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:43.0) Gecko/20100101 Firefox/43.0'),
            ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
            ('Accept-Language', 'en-US,en;q=0.5'),
            ('Accept-Encoding', 'gzip, deflate'),]
        # extract source_id from main page
        print '--------Extracting event source id------------'
        event_location_req = opener.open(url)
        event_location = event_location_req.info().getheader('Location')
        for user in namespace.users:
            event_content_req = opener.open(event_location)
            event_content = zlib.decompress(event_content_req.read(), 16+zlib.MAX_WBITS)
            source_id_index = event_content.index("source_id")
            source_id = event_content[source_id_index + 18:source_id_index + 50]
            quantity_id_index = event_content.index("show_ticket_selection")
            quantity_id = event_content[quantity_id_index + 50:quantity_id_index + 58]
            print 'source_id : ' + source_id
            # send orderstart
            print '--------Sending order start request-----------'
            data = "eid=" + namespace.eid + "&has_javascript=1&source_id=" + source_id + \
                   "&payment_type=free&legacy_event_page=1&invite=&affiliate=ehomecard&referrer=&referral_code=&w=&waitlist_code=&eventpassword=&discount=&quant_" + quantity_id + "_None=1"
            "&payment_type=free&legacy_event_page=1&invite=&affiliate=ehomecard&referrer=&referral_code=&w=&waitlist_code=&eventpassword=&discount=&quant_" + quantity_id + "_None=1"
        opener.addheaders += [('Referer', url), ]
        orderstart_req = opener.open("https://www.eventbrite.fr/orderstart", data)
        orderstart_resp = orderstart_req.info()
        register_url = orderstart_resp.getheader("Location")
        print 'register_url : ' + register_url
        # register
        print '----------Perform registration---------------'
        user_info = user.split(' ')
        register_data = "submitted=1&ismanual=&payment_type=free&crumb=ab1f130a1d8d37&w=&_nomo=&first_name=" + \
                        user_info[
                            0] + "&last_name=" + user_info[
                            1] + "&email_address=" + user_info[2] + "&confirm_email_address=" + user_info[
                            2] + "&passwd="
        register_req = opener.open(register_url, register_data)


def main():
    parser = argparse.ArgumentParser(description='Eventbrite ticket bot.')
    parser.add_argument('-i', '--eid', action=ArgHandler, type=int, required=True, help='Set event eid.')
    parser.add_argument('-u', '--users', action=ArgHandler, type=argparse.FileType('r'), required=True,
                        help='Set users file with the format \'LastName FirstName Email\'.')
    parser.add_argument('-d', '--dump', action=ArgHandler, help='Retreive ticket.')
    args = parser.parse_args()


if __name__ == "__main__":
    main()
