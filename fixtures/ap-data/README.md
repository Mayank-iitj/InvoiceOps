# ap-data — Invoice Mismatch Exception Room

Fictional buyer, 5 vendors, 12 pending invoices (+1 already paid). Currency INR, GST 18%.
Matching key: invoice_headers.po_id -> po_lines -> goods_receipts / delivery_challans (by po_id, sku).
Match on pre-GST amounts. Prior billing against a PO = all other invoices (including paid) on the same po_id.
Files: vendors, price_list (date-effective), po_lines, goods_receipts, delivery_challans,
invoice_headers, invoice_lines, vendor_history, roles, room_rules, scripted_human_replies (test only).
