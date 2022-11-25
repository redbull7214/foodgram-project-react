from django.http import FileResponse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def get_shopping_cart(ingredients):
    """
    Функция для генерации pdf.
    """
    pdfmetrics.registerFont(
        TTFont('Lemon', 'data/Lemon.ttf', 'UTF-8'))

    # response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = ('attachment; '
    #                                    'filename="shopping_list.pdf"')
    page = canvas.Canvas('shopping_list.pdf')
    page.setFont('Lemon', size=24)
    page.drawString(200, 800, 'Список покупок')
    page.setFont('Lemon', size=16)
    height = 750
    for value in ingredients:
        page.drawString(75, height, (
            value['ingredient__name'] + ' - '
            + str(value['quantity']) + ' '
            + value['ingredient__measurement_unit']
        ))
        height -= 25
    page.showPage()
    page.save()
    return FileResponse(page, as_attachment=True, filename='shopping_list.pdf')
