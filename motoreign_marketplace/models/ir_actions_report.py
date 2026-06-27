# -*- coding: utf-8 -*-
# Motoreign Multi Vendor Marketplace - Odoo 19
# License LGPL-3.0

import base64
import io
import logging

from odoo import models
from odoo.tools.pdf import PdfFileWriter

_logger = logging.getLogger(__name__)


class IrActionsReport(models.Model):
    """Fixes PDF rendering for sale orders with quote builder attachments"""
    _inherit = 'ir.actions.report'

    def _render_qweb_pdf_prepare_streams(self, report_ref, data, res_ids=None):
        """Override to safely handle PDF form field filling errors"""
        try:
            from odoo.addons.sale_pdf_quote_builder.models.ir_actions_report import (
                IrActionsReport as SaleQuoteReport,
            )
            result = super(SaleQuoteReport, self)._render_qweb_pdf_prepare_streams(
                report_ref, data, res_ids=res_ids)
        except Exception:
            # Fallback: call standard render without the quote builder logic
            result = super()._render_qweb_pdf_prepare_streams(
                report_ref, data, res_ids=res_ids)
            return result

        report = self._get_report(report_ref)
        if report.report_name != 'sale.report_saleorder':
            return result

        orders = self.env['sale.order'].browse(res_ids)
        for order in orders:
            initial_stream = result.get(order.id, {}).get('stream')
            if not initial_stream:
                continue
            order_tmpl = order.sale_order_template_id
            header_rec = order_tmpl if order_tmpl and order_tmpl.sale_header else order.company_id
            footer_rec = order_tmpl if order_tmpl and order_tmpl.sale_footer else order.company_id
            has_header = bool(getattr(header_rec, 'sale_header', False))
            has_footer = bool(getattr(footer_rec, 'sale_footer', False))

            included_docs = self.env['product.document']
            doc_line_map = {}
            for line in order.order_line:
                docs = (
                    line.product_id.product_document_ids.filtered(
                        lambda d: d.attached_on == 'inside')
                    or line.product_template_id.product_document_ids.filtered(
                        lambda d: d.attached_on == 'inside')
                )
                included_docs |= docs
                doc_line_map.update({d.id: line.id for d in docs})

            if not has_header and not included_docs and not has_footer:
                continue

            writer = PdfFileWriter()
            if has_header:
                self._add_pages_to_writer(writer, base64.b64decode(header_rec.sale_header))
            for doc in included_docs:
                self._add_pages_to_writer(writer, base64.b64decode(doc.datas),
                                          doc_line_map[doc.id])
            self._add_pages_to_writer(writer, initial_stream.getvalue())
            if has_footer:
                self._add_pages_to_writer(writer, base64.b64decode(footer_rec.sale_footer))

            form_fields = self._get_form_fields_mapping(order, doc_line_map)
            try:
                from odoo.tools import pdf as pdf_tools
                pdf_tools.fill_form_fields_pdf(writer, form_fields=form_fields)
            except Exception as e:
                _logger.warning("Could not fill PDF form fields for order %s: %s",
                                order.name, e)

            with io.BytesIO() as buf:
                writer.write(buf)
                result[order.id]['stream'] = io.BytesIO(buf.getvalue())

        return result
