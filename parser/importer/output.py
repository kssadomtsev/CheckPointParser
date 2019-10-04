import xlsxwriter


def print_to_xlsx(dict, filename):
    workbook = xlsxwriter.Workbook("..\\logs\\" + filename)
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': True})
    cell_format = workbook.add_format({'text_wrap': True})
    worksheet.write('A1', 'Object', bold)
    worksheet.write('B1', 'Info', bold)
    row = 1
    for key, value in dict.items():
        worksheet.write(row, 0, str(key))
        worksheet.write(row, 1, value)
        row += 1
    workbook.close()