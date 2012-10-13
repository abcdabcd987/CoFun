import web

web.config.debug = False
render = web.template.render('Templates/')

CONFIG = {
    'dbtype':       'mysql',
    'dbuser':       'root',
    'dbpasswd':     '123456',
    'dbname':       'cofun',
}
