const CACHE="acpa-field-v2";
const SHELL=["./index.html","./style.css","./app.js","./manifest.webmanifest","./icon.svg"];
self.addEventListener("install",event=>event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(SHELL))));
self.addEventListener("activate",event=>event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith("acpa-field-")&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener("fetch",event=>{
 const req=event.request,url=new URL(req.url),scope=new URL(self.registration.scope);
 if(req.method!=="GET"||url.origin!==scope.origin||!url.pathname.startsWith(scope.pathname))return;
 const allowed=SHELL.map(path=>new URL(path,scope).pathname);
 if(req.mode==="navigate"){
   event.respondWith(fetch(req).catch(()=>caches.open(CACHE).then(c=>c.match(new URL("./index.html",scope)))));
 }else if(allowed.includes(url.pathname)){
   event.respondWith(caches.open(CACHE).then(c=>c.match(req,{ignoreSearch:true})).then(r=>r||fetch(req)));
 }
});
