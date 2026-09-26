const http=require('http'),fs=require('fs'),path=require('path');
const root=__dirname,port=process.env.PORT||3000;
const types={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json; charset=utf-8','.webmanifest':'application/manifest+json; charset=utf-8','.png':'image/png','.svg':'image/svg+xml; charset=utf-8'};
http.createServer((req,res)=>{
  let p=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
  if(p==='/'||p==='')p='/index.html';
  const file=path.normalize(path.join(root,p));
  if(!file.startsWith(root)){res.writeHead(403);return res.end('Forbidden')}
  fs.readFile(file,(err,data)=>{
    if(err){res.writeHead(404,{'Content-Type':'text/plain; charset=utf-8'});return res.end('Not found')}
    res.writeHead(200,{
      'Content-Type':types[path.extname(file)]||'application/octet-stream',
      'Cache-Control':path.basename(file)==='index.html'?'no-cache':'public, max-age=3600',
      'X-Content-Type-Options':'nosniff',
      'Referrer-Policy':'no-referrer',
      'Permissions-Policy':'camera=(), microphone=(), geolocation=(self)',
      'Content-Security-Policy':"default-src 'self'; img-src 'self' data: https://www.openstreetmap.org https://*.tile.openstreetmap.org; frame-src https://www.openstreetmap.org; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self';"
    });
    res.end(data);
  });
}).listen(port,'0.0.0.0',()=>console.log('Family Guard Pro listening on '+port));