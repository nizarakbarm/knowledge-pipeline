- OpenSuse Leap 6.0
- OpenLitespeed 1.8.5
- New STD C, need patch
### nspersist_init() function def error
- Error npersiste_init function def
	- gcc version gcc (SUSE Linux) 15.1.1 20250714 with std version 202311L (ISO C23)
	- Definition npersist_init() at header src/extensions/cgi/nspersist.h
	```C
	/**
 * @fn nspersist_init
 * @brief Should only be called by nsinit, initializes persistence.
 * @return 0 if no error; -1 if an error.
 **/
int nspersist_init();
	```
	- But definition with function body at src/extensions/cgi/nspersist.c
	```C
	int nspersist_init(lscgid_t *pCGI)
{
    char *vhenv = ns_getenv(pCGI, LS_NS_VHOST);
    int rc = nspersist_setvhost(vhenv);
    return rc;
}
	```
	- Change `int nspersist_init();` to `int nspersist_init(lscgid_t *pCGI)` in src/extensions/cgi/nspersist.h to follow std c with version larger than 13

- Misc error:
````
/root/openlitespeed-1.8.5/src/extensions/cgi/nsnosandbox.c: In function ‘open_nosandbox_socket’:
/root/openlitespeed-1.8.5/src/extensions/cgi/nsnosandbox.c:670:9: error: too many arguments to function ‘ns_done’; expected 0, have 1
  670 |         ns_done(0);
      |         ^~~~~~~ ~
In file included from /root/openlitespeed-1.8.5/src/extensions/cgi/nsnosandbox.c:26:
/root/openlitespeed-1.8.5/src/extensions/cgi/ns.h:120:6: note: declared here
  120 | void ns_done();
      |      ^~~~~~~
/root/openlitespeed-1.8.5/src/extensions/cgi/nsnosandbox.c:695:9: error: too many arguments to function ‘ns_done’; expected 0, have 1
  695 |         ns_done(0);
      |         ^~~~~~~ ~
/root/openlitespeed-1.8.5/src/extensions/cgi/ns.h:120:6: note: declared here
  120 | void ns_done();
      |      ^~~~~~~
/root/openlitespeed-1.8.5/src/extensions/cgi/nsnosandbox.c:703:9: error: too many arguments to function ‘ns_done’; expected 0, have 1
  703 |         ns_done(0);
      |         ^~~~~~~ ~
/root/openlitespeed-1.8.5/src/extensions/cgi/ns.h:120:6: note: declared here
  120 | void ns_done();
      |      ^~~~~~~
/root/openlitespeed-1.8.5/src/extensions/cgi/nsnosandbox.c:713:9: error: too many arguments to function ‘ns_done’; expected 0, have 1
  713 |         ns_done(0);
      |         ^~~~~~~ ~
/root/openlitespeed-1.8.5/src/extensions/cgi/ns.h:120:6: note: declared here
  120 | void ns_done();
      |      ^~~~~~~
/root/openlitespeed-1.8.5/src/extensions/cgi/nsnosandbox.c:718:9: error: too many arguments to function ‘ns_done’; expected 0, have 1
  718 |         ns_done(0);
      |         ^~~~~~~ ~
/root/openlitespeed-1.8.5/src/extensions/cgi/ns.h:120:6: note: declared here
  120 | void ns_done();
      |      ^~~~~~~
/root/openlitespeed-1.8.5/src/extensions/cgi/nsnosandbox.c: In function ‘save_links’:
/root/openlitespeed-1.8.5/src/extensions/cgi/nsnosandbox.c:736:13: error: too many arguments to function ‘ns_done’; expected 0, have 1
  736 |             ns_done(0);
      |             ^~~~~~~ ~
/root/openlitespeed-1.8.5/src/extensions/cgi/ns.h:120:6: note: declared here
  120 | void ns_done();
      |      ^~~~~~~
/root/openlitespeed-1.8.5/src/extensions/cgi/nsnosandbox.c:765:21: error: too many arguments to function ‘ns_done’; expected 0, have 1
  765 |                     ns_done(0);
      |                     ^~~~~~~ ~
/root/openlitespeed-1.8.5/src/extensions/cgi/ns.h:120:6: note: declared here
  120 | void ns_done();
      |      ^~~~~~~
/root/openlitespeed-1.8.5/src/extensions/cgi/nsnosandbox.c: In function ‘read_hostexec_files’:
/root/openlitespeed-1.8.5/src/extensions/cgi/nsnosandbox.c:796:13: error: too many arguments to function ‘ns_done’; expected 0, have 1
  796 |             ns_done(0);
      |             ^~~~~~~ ~
/root/openlitespeed-1.8.5/src/extensions/cgi/ns.h:120:6: note: declared here
  120 | void ns_done();
      |      ^~~~~~~
/root/openlitespeed-1.8.5/src/extensions/cgi/nsnosandbox.c:803:13: error: too many arguments to function ‘ns_done’; expected 0, have 1
  803 |             ns_done(0);
      |             ^~~~~~~ ~
/root/openlitespeed-1.8.5/src/extensions/cgi/ns.h:120:6: note: declared here
  120 | void ns_done();
      |      ^~~~~~~
/root/openlitespeed-1.8.5/src/extensions/cgi/nsnosandbox.c:811:17: error: too many arguments to function ‘ns_done’; expected 0, have 1
  811 |                 ns_done(0);
      |                 ^~~~~~~ ~
/root/openlitespeed-1.8.5/src/extensions/cgi/ns.h:120:6: note: declared here
  120 | void ns_done();
      |      ^~~~~~~
```