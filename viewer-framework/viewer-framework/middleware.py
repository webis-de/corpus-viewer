from django.db import connection

class SqlPrintMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        sqltime = 0 # Variable to store execution time
        counter = 0
        print('___________________________________________________________')
        for query in connection.queries:
            if query['sql'] != 'BEGIN':
                counter += 1
                # print(query['time'])
                sqltime += float(query["time"])  # Add the time that the query took to the total
                # print(query['sql'])
                # print('-----------------------------------------------------------')

        # # len(connection.queries) = total number of queries
        print('-----------------------------------------------------------')
        print("Page render: " + str(sqltime) + " sec for " + str(counter) + " queries")
        print('___________________________________________________________')

        return response


# from django.conf import settings

# class MultiPortMiddleware(object):
#     def __init__(self, get_response):
#         self.get_response = get_response
#     """
#     Middleware changes the SESSION_COOKIE_NAME to use the current port in the name
#     """

#     def __call__(self, request):
#         response = self.get_response(request)
#         settings.SESSION_COOKIE_NAME = 'sessionid_{}'.format(request.META['SERVER_PORT'])
#         settings.CSRF_COOKIE_NAME = 'csrftoken_{}'.format(request.META['SERVER_PORT'])
#         return response