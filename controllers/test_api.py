from odoo import http


class TestApi(http.Controller):

    @http.route('/api/test',methods=['GET'],auth='none',type='http',csrf=False)
    def test_endpoint(self):
        print("in endpoint")