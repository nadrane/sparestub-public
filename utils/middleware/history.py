class LastVisitedMiddleware(object):
    """
    This middleware maintains a history of what url the user last visited.
    It's used so that we know where to redirect a user after login.
    """

    def process_request(self, request):
        request_path = request.get_full_path()
        request.session['last_visited'] = request.session.get('currently_visiting', '')
        request.session['currently_visiting'] = request_path