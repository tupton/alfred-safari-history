#!/usr/bin/env python

"""
select history_items.id, url, title from history_items inner join history_visits on
history_visits.history_item = history_items.id where url like '%github%' group by url order by
visit_count desc, visit_time desc limit 10;
"""
