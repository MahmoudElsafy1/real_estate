import json

from odoo import http
from odoo.http import request


class PropertyApi(http.Controller):



    @http.route('/v1/property',methods=['POST'],auth='none',type='http',csrf=False)
    def  post_property(self):
        args=request.httprequest.data.decode()
        vals=json.loads(args)
        res=request.env['property'].sudo().create(vals)
        if res:
            return request.make_json_response({
                'message':'property has been created'
            },status=200)



