def isProductSubscribed(productId):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""select * from subscriptions where username = '%s'""" % session['username'])

    existingsub = cur.fetchone()

    if existingsub > 0:
        return existingsub['productid']
    else:
        return 'Subscription does not already exist'
