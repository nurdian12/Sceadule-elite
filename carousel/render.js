// usage: node render.js file1.html file2.html ...  -> writes .jpg next to each html
const {chromium}=require('playwright');
(async()=>{
 const b=await chromium.launch();
 const p=await b.newPage({viewport:{width:1080,height:1350}});
 for(const f of process.argv.slice(2)){
  await p.goto('file://'+f);
  const el=await p.$('.s');
  await el.screenshot({path:f.replace(/\.html$/,'.jpg'),type:'jpeg',quality:88});
 }
 await b.close();
})();
