# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from pybooru import Danbooru

client = Danbooru('danbooru', username='dough-dev', api_key='UA8jEn4MjJJy5cG2waZPJpaU')
response = client.comment_create(post_id=id, body='fumino')

print(client.last_call)
