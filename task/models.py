from django.db import models
from django.utils import timezone



class ClickEvent(models.Model):
    page_name = models.CharField(max_length=1000)
    page_section_name = models.CharField(max_length=1000)
    clicked_element_name = models.CharField(max_length=1000)
    clicked_element_type = models.CharField(max_length=1000)
    time_spent_on_page = models.CharField(max_length=1000)
    click_date = models.DateTimeField(default=timezone.now)
    # click_time = models.DateTimeField(auto_now_add=False)
    city = models.CharField(max_length=1000, null=True)
    region = models.CharField(max_length=1000, null=True)
    country = models.CharField(max_length=1000, null=True)

    class Meta:
        db_table = 'click_events'
    
    def __str__(self):
        return self.page_name + " - " + self.page_section_name + " - " + self.clicked_element_name + " - " + self.clicked_element_type + " - " + self.time_spent_on_page
    

