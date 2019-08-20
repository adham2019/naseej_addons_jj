# -*- coding: utf-8 -*-

from odoo import models, fields, api


class NaseejInventory(models.Model):
    _inherit = 'stock.picking.type'

    internal_loc = fields.Boolean('Is Internal?')
    internal_location = fields.Many2one('stock.location', string='Destination Transfer Location')
    internal_operation_type = fields.Many2one('stock.picking.type', string='Internal Operation Type')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    pack_picking_id = fields.Many2one('stock.picking', 'Pack Picking')
    show_button_generate = fields.Boolean(string="show", default=True)
    after_click_button_generate = fields.Boolean(string="click", default=True)
    check_operation_type = fields.Boolean(string="click", default=True)

    @api.onchange('picking_type_id')
    def _check_operation_type(self):
        for pick in self:
            if pick.picking_type_id.code != 'internal':
                self.check_operation_type = False

    @api.onchange('picking_type_id')
    def show_generate_btn(self):
        for pick in self:
            if not pick.picking_type_id.internal_loc:
                self.show_button_generate = False

    # @api.onchange('picking_type_id', 'partner_id')
    # def onchange_picking_type_id_inter(self):
    #     for pick in self:
    #         if pick.picking_type_id.internal_loc:
    #             pick.location_dest_id = pick.picking_type_id.internal_location

    def generate_receipt_order(self):
        pick = self.copy()
        internal_picking_type = self.picking_type_id.internal_operation_type
        pick_dest_location = self.picking_type_id.internal_location
        pick.write({'picking_type_id': internal_picking_type.id,
                    'location_id': self.location_dest_id.id,
                    'location_dest_id': pick_dest_location.id, })
        for line in pick.move_lines:
            line.write({
                'picking_type_id': internal_picking_type.id,
                'picking_id': pick.id,
                'location_id': self.location_dest_id.id,
                'location_dest_id': pick_dest_location.id

            })

        pick.action_confirm()
        pick.action_assign()
        pick.show_button_generate = False
        self.after_click_button_generate = False
        self.pack_picking_id = pick.id


