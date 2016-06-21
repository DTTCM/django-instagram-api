import re
import simplejson as json
from oauth_tokens.providers.instagram import InstagramAuthRequest


class GraphQL(object):

    url = 'https://www.instagram.com/query/'
    cookie = "Cookie': '__utma=227057989.1129888433.1423302270.1433340455.1434559808.20; __utmc=227057989; mid=VpvY_gAEAAHrA7w3K-gGUZNO3gUn; sessionid=IGSCba3ae99bb688d697f6f84680fe5287a9627652d6b61b622cedec5a82789859d1%3AMP0evk4Yn1zzZ4LeUuqftzm8qDWN90Ce%3A%7B%22_token_ver%22%3A2%2C%22_auth_user_id%22%3A1692711770%2C%22_token%22%3A%221692711770%3AcH25i1BtKesyunRKLY0OcpzdAWHsbNvr%3A6773d2007cb9f6a25278f4282c5ee165bad90e216bc0f3719777770c1c2f35fe%22%2C%22asns%22%3A%7B%22time%22%3A1466446252%2C%2283.220.237.174%22%3A16345%7D%2C%22_auth_user_backend%22%3A%22accounts.backends.CaseInsensitiveModelBackend%22%2C%22last_refreshed%22%3A1466446574.261982%2C%22_platform%22%3A4%2C%22_auth_user_hash%22%3A%22%22%7D; ig_pr=2; ig_vw=1618; s_network=; csrftoken=CSRF_TOKEN; ds_user_id=1692711770"
    # headers = {
    #     # 'X-Instagram-AJAX': 1,
    #     # 'Origin': 'https://www.instagram.com',
    #     # 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36',
    #     # 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    #     # 'Accept': '*/*', 'X-DevTools-Emulate-Network-Conditions-Client-Id': 'ED52586A-6195-44F6-A073-5DD990EB2D8B',
    #     # 'X-Requested-With': 'XMLHttpRequest',
    #     'X-CSRFToken': 'yNItV0otcJfKN9zsJjqsxPKDEZemOvkQ',
    #     'Referer': 'https://www.instagram.com/%s/' % user.username,
    #     # 'Accept-Encoding': 'gzip, deflate, br',
    #     # 'Accept-Language': 'en-US,en;q=0.8,ru;q=0.6',
    #     'Cookie': '__utma=227057989.1129888433.1423302270.1433340455.1434559808.20; __utmc=227057989; mid=VpvY_gAEAAHrA7w3K-gGUZNO3gUn; sessionid=IGSCba3ae99bb688d697f6f84680fe5287a9627652d6b61b622cedec5a82789859d1%3AMP0evk4Yn1zzZ4LeUuqftzm8qDWN90Ce%3A%7B%22_token_ver%22%3A2%2C%22_auth_user_id%22%3A1692711770%2C%22_token%22%3A%221692711770%3AcH25i1BtKesyunRKLY0OcpzdAWHsbNvr%3A6773d2007cb9f6a25278f4282c5ee165bad90e216bc0f3719777770c1c2f35fe%22%2C%22asns%22%3A%7B%22time%22%3A1466446252%2C%2283.220.237.174%22%3A16345%7D%2C%22_auth_user_backend%22%3A%22accounts.backends.CaseInsensitiveModelBackend%22%2C%22last_refreshed%22%3A1466446574.261982%2C%22_platform%22%3A4%2C%22_auth_user_hash%22%3A%22%22%7D; ig_pr=2; ig_vw=1618; s_network=; csrftoken=yNItV0otcJfKN9zsJjqsxPKDEZemOvkQ; ds_user_id=1692711770'
    # }

    def related_users(self, endpoint, user):
        req = InstagramAuthRequest()
        url = 'https://www.instagram.com/%s/' % user.username
        response = req.authorized_request('get', url=url)
        csrf_token = re.findall(r'"csrf_token": "([^"]+)"}', response.content)[0]
        headers = {
            'Referer': url,
            'X-CSRFToken': csrf_token,
            'Cookie': self.cookie.replace('CSRF_TOKEN', csrf_token)
        }

        user_id = user.id
        limit = 100
        method = 'first'
        args = limit
        next_page = True

        while next_page:

            graphql = '''
ig_user(%(user_id)s) {
    %(endpoint)s.%(method)s(%(args)s) {
        count, page_info { end_cursor, has_next_page },
        nodes { id, is_verified, followed_by_viewer, requested_by_viewer, full_name, profile_pic_url, username }
    }
}''' % locals()

            response = req.authorized_request('post', url=self.url, data={'q': graphql}, headers=headers)
            # print graphql, response.content
            json_response = json.loads(response.content)

            method = 'after'
            args = '%s, %s' % (json_response[endpoint]['page_info']['end_cursor'], limit)
            next_page = json_response[endpoint]['page_info']['has_next_page']
            # print json_response[endpoint]['count'], cursor, next_page
            yield json_response[endpoint]['nodes']
