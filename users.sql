UPDATE res_users SET active=false WHERE id in (665, 630, 563, 693, 760, 772, 631, 534, 686, 453, 658, 723, 81, 412, 384, 336, 651, 138, 548, 711, 364, 62, 469, 553, 205, 687, 652, 656, 777, 154, 348, 747, 765, 262, 634, 164, 635, 638, 713, 530);
UPDATE res_users SET active=false WHERE company_id=3;

UPDATE resource_resource SET active=false WHERE user_id in (SELECT id FROM res_users WHERE id in (665, 630, 563, 693, 760, 772, 631, 534, 686, 453, 658, 723, 81, 412, 384, 336, 651, 138, 548, 711, 364, 62, 469, 553, 205, 687, 652, 656, 777, 154, 348, 747, 765, 262, 634, 164, 635, 638, 713, 530)) or company_id=3;
UPDATE resource_resource SET company_id=4 WHERE company_id=1;