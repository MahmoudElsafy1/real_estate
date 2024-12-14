

from odoo import models,fields,api
from odoo.exceptions import ValidationError
from odoo.fields import Datetime


class Property(models.Model):
    _name = 'property'
    _description='Property'
    _inherit = ['mail.thread','mail.activity.mixin']
    ref=fields.Char(default='New',readonly=True)
    name=fields.Char(required=True,default="new",size=12)
    description=fields.Text(tracking=1)
    postcode=fields.Char(required=True)
    date_availability=fields.Date( default=Datetime.now(),tracking=1)
    expected_selling_date=fields.Date(tracking=1)
    is_late=fields.Boolean()
    expected_price=fields.Float()
    selling_price=fields.Float()
    diff=fields.Float(compute="_compute_diff", store=1)
    bedrooms=fields.Integer()
    living_area=fields.Integer()
    facades=fields.Integer()
    garage=fields.Boolean()
    garden=fields.Boolean()
    garden_area=fields.Boolean()
    garden_orientation=fields.Selection([('north','North'),
                                         ('south', 'South'),
                                         ('east', 'East'),
                                         ('west', 'West') ],default="west")
    state=fields.Selection([
        ('draft','Draft'),
        ('pending','Pending'),
        ('sold','Sold'),
        ('closed', 'Closed'),
    ],default="draft")

    owner_id=fields.Many2one('owner')
    tag_ids=fields.Many2many('tag')
    owner_address=fields.Char(related='owner_id.address')
    owner_phone = fields.Char(related='owner_id.phone')

    line_ids=fields.One2many('property.line','property_id')

    active=fields.Boolean(default=True)
    _sql_constraints = [
        ('unique_name','unique("name")','the name is exit')
    ]
    @api.depends('expected_price','selling_price','owner_id.phone')
    def _compute_diff(self):
        for rec in self:
            print( "inside _compute_diff")
            rec.diff=rec.expected_price-rec.selling_price

    @api.onchange('expected_price')
    def _onchange_expected_price(self):
        for rec in self:
            print("inside onchange method")
            return {
                'warning':{
                    'title':'warning','message':'negative value.','type':'notification'
                }
            }



    @api.constrains('bedrooms')
    def _check_badroom_greater_zero(self):
        for rec in self:
            if rec.bedrooms==0:
                raise ValidationError("Please add valid number")

    def action_draft(self):
        for rec in self:
            rec.create_property_history_record(rec.state,'draft')
            rec.state='draft'

    def action_pending(self):
        for rec in self:
            rec.create_property_history_record(rec.state,'pending')
            rec.state='pending'

    def action_sold(self):
        for rec in self:
            rec.create_property_history_record(rec.state,'sold')
            rec.state='sold'

    def action_closed(self):
        for rec in self:
            rec.create_property_history_record(rec.state,'closed')
            rec.state='closed'

    def check_expected_selling_date(self):
        property_ids=self.search([])
        for rec in property_ids:
            if rec.expected_selling_date and rec.expected_selling_date<fields.Date.today():
                rec.is_late=True



    def action(self):
        print(self.env['owner'].search([]))

    @api.model
    def create(self, vals):
        res=super(Property, self).create(vals)
        if res.ref=='New':
           res.ref=self.env['ir.sequence'].next_by_code('property_seq')

        return res
    def create_property_history_record(self,old_state,new_state,reason=""):
        for rec in self:
            rec.env['property.history'].create({
                'user_id':rec.env.uid,
                'property_id':rec.id,
                'old_state':old_state,
                'new_state':new_state,
                'reason':reason or '',
                'line_ids':[(0,0,{'description':line.description,'area':line.area})for line in rec.line_ids]


            })


    def action_change_state_wizard(self):
        action=self.env['ir.actions.actions']._for_xml_id('app_one.change_state_wizard_action')
        action['context']={'default_property_id':self.id}
        return action

    def action_open_related_owner(self):
        action=self.env['ir.actions.actions']._for_xml_id('app_one.owner_action')
        view_id=self.env.ref('app_one.owner_view_form').id
        action['res_id']=self.owner_id.id
        action['views']=[[view_id,'form']]
        return action






    # @api.model_create_multi
    # def create(self, vals):
    #     res=super(Property,self).create(vals)
    #     print("in create oprion")
    #     return res
    #
    #
    # @api.model
    # def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
    #     res=super(Property,self)._search(domain, offset=0, limit=None, order=None, access_rights_uid=None)
    #     print("in search methods")
    #     return res
    #
    # def write(self, vals):
    #     res=super(Property,self).write(vals)
    #     print("in write methods")
    #     return res
    #
    # def unlink(self):
    #     res=super(Property,self).unlink()
    #     print( "in unlink methods")
    #     return  res
    #


class PropertyLine(models.Model):
    _name = 'property.line'

    area=fields.Float()
    description=fields.Char()

    property_id=fields.Many2one('property')






