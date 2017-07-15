#!python

from sexpdata import loads,dumps,car,cdr
import httplib
import ssl
import os

archive_conns = {
"marmalade": httplib.HTTPSConnection("marmalade-repo.org", context=ssl._create_unverified_context()),
"elpa": httplib.HTTPConnection("elpa.gnu.org"),
"melpa": httplib.HTTPConnection("melpa.org")
}

for repo_name, conn in archive_conns.iteritems():
    conn.connect()
    conn.request("GET", "/packages/archive-contents")
    response = conn.getresponse()

    if response.status == 200:
        data = response.read()
        conn.close()
        archive_list = loads(data)
        package_list = cdr(archive_list)

        for package in package_list:
            name = package[0].value()
            version_array = car(package[2].value())
            version = ".".join(map(lambda x: str(x), version_array))

            package_type = package[2].value()[3].value()
            extension = {"single": "el",
                         "tar": "tar"}.get(package_type)
            filename = "%s-%s.%s" % (name, version, extension)
            package_uri = "/packages/%s" % (filename)

            conn.connect()
            conn.request("GET", package_uri)
            package_response = conn.getresponse()
            if package_response.status != 200:
                print "error getting %s - got %s" % (name, package_response.status)
            else:
                package_contents = package_response.read()
                
                try:
                    os.makedirs("packages/%s" % (repo_name))
                except:
                    pass

                fd = open("packages/%s/%s" % (repo_name, filename), "w")
                fd.write(package_contents)
                fd.flush()
                fd.close()

            conn.close()

# end
