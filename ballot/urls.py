from django.contrib import admin
from django.urls import path

from ballot import views

urlpatterns = [
    path('vote/', views.submit_vote),
    path('seal/', views.seal),

    path('transactions/', views.transactions),
    path('block/<str:block_hash>/', views.block_detail),

    path('sync_block/<int:block_id>/', views.sync_block),
    path('blockchain/', views.blockchain),

    path('verify/', views.verify),
    path('sync/', views.sync),
]

