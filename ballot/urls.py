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

"""

username ->  cQlUC1zRPO
password ->  ha6dCtdHF8

-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgFGP9QcdXa5UnuS3K
8liJpcMir0xlO8Hts2BnUME6FXWhRANCAAS/xfHlBJzs7Dict6vwDSqerkqlY7zr
yG14RyNIf4kpN2bQMl25ulLjsQ2raRpr9AHWN6+W9wMRlsvUOwezPjLX
-----END PRIVATE KEY-----


username ->  BJa3NLEs0y
password ->  jmP9ebAhMd
*********private key*******
-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgU161NeHJqBo4aKGd
YLts/05ML8jET7aJ2m1pWAA6gUuhRANCAAQLJdYoyAByIkEuNOHYzHAgcX+019XG
EnVoVRXDpQNzdLoIMheGbKTVAKHma3ZoGCdk/s3Mn128Ampw7XEyVziq
-----END PRIVATE KEY-----
***************

-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAECyXWKMgAciJBLjTh2MxwIHF/tNfV
xhJ1aFUVw6UDc3S6CDIXhmyk1QCh5mt2aBgnZP7NzJ9dvAJqcO1xMlc4qg==
-----END PUBLIC KEY-----
***************


username ->  zN4ixOGyIt
password ->  59QfZmPxP5
*********private key*******
-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgeyMRuQw2u3+ZAkJG
m9W8woJYcGqBR88UWYJ/rNXR/4yhRANCAATa/xE6fJIZiN6z4jDZdP13cLUdzP5Z
EuiO7pgyzoQGFgnG+3HqlKWnXA2XnvtMMZsfRs8GhnAfjS7rndYXlsj5
-----END PRIVATE KEY-----
***************


"""
