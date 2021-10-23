import io
from flask import send_file
import pandas as pd


def download_data(dataframe, attachment_filename):
    buf = io.BytesIO()
    excel_writer = pd.ExcelWriter(buf, engine="xlsxwriter")
    dataframe.to_excel(excel_writer, sheet_name="Sheet1", index=False)
    excel_writer.save()
    excel_data = buf.getvalue()
    buf.seek(0)

    return send_file(
        buf,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        attachment_filename=attachment_filename,
        as_attachment=True,
        cache_timeout=0,
    )
