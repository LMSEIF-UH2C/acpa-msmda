"use strict";
const $=id=>document.getElementById(id);
const v=$("video");
let url=null,markers=[],lang="fr";
const keys=["title","language","privacy","open","speed","mark","close","step","feedback","observation","export","limits","invalid","ready","discard","remove","jump","empty","error"];
const dict={
fr:["Feedback vidéo pédagogique","Langue","La vidéo est lue dans ce navigateur, sans téléversement. Respectez les autorisations de captation et ne saisissez aucun nom d'élève.","Ouvrir une vidéo locale","Vitesse de lecture","Ajouter un repère","Fermer la vidéo","Déplacement temporel approximatif, sans garantie d'image exacte.","Repères et feedback","Observation pédagogique","Exporter les observations","Les repères restent en mémoire jusqu'à la fermeture de la vidéo ou de la page. L'export contient uniquement les temps et les observations, pas la vidéo.","Fichier vidéo invalide.","Vidéo prête.","Abandonner les repères non exportés ?","Supprimer","Revenir au repère","Aucun repère.","Format vidéo non pris en charge par ce navigateur."],
en:["Teaching video feedback","Language","Video plays locally without upload. Respect recording permissions and do not enter pupil names.","Open local video","Playback speed","Add marker","Close video","Approximate time step, not guaranteed frame-accurate.","Markers and feedback","Teaching observation","Export observations","Markers stay in memory until the video or page is closed. Export contains timestamps and observations only, not video.","Invalid video file.","Video ready.","Discard markers?","Remove","Seek to marker","No markers.","Video format not supported by this browser."],
ar:["التغذية الراجعة بالفيديو","اللغة","يُشغّل الفيديو محليا دون رفعه. احترم تراخيص التصوير ولا تدخل أسماء التلاميذ.","فتح فيديو محلي","سرعة التشغيل","إضافة علامة زمنية","إغلاق الفيديو","تنقل زمني تقريبي دون ضمان دقة الإطار.","العلامات والتغذية الراجعة","ملاحظة تربوية","تصدير الملاحظات","تبقى العلامات في الذاكرة حتى إغلاق الفيديو أو الصفحة. يتضمن التصدير الأوقات والملاحظات فقط دون الفيديو.","ملف فيديو غير صالح.","الفيديو جاهز.","حذف العلامات؟","حذف","الانتقال إلى العلامة","لا توجد علامات.","صيغة الفيديو غير مدعومة في هذا المتصفح."]};
const t=k=>dict[lang][keys.indexOf(k)]||k;
function ready(){return url!==null&&Number.isFinite(v.duration)&&v.duration>0;}
function controls(){for(const id of ["prev","next","mark"])$(id).disabled=!ready();$("close").disabled=!url;$("export").disabled=!markers.length;}
function render(){const list=$("markers");list.replaceChildren();for(const m of markers){const li=document.createElement("li");const jump=document.createElement("button");jump.textContent=m.seconds.toFixed(2)+" s";jump.setAttribute("aria-label",t("jump")+" "+jump.textContent);jump.onclick=()=>seek(m.seconds);const note=document.createElement("span");note.textContent=m.observation;const remove=document.createElement("button");remove.textContent=t("remove");remove.onclick=()=>{markers=markers.filter(x=>x!==m);render();};li.append(jump,note,remove);list.append(li);}controls();}
function translate(){document.documentElement.lang=lang;document.documentElement.dir=lang==="ar"?"rtl":"ltr";document.querySelectorAll("[data-i]").forEach(e=>e.textContent=t(e.dataset.i));render();}
$("lang").onchange=e=>{lang=e.target.value;translate();};
function clear(){v.pause();v.removeAttribute("src");v.load();if(url)URL.revokeObjectURL(url);url=null;markers=[];$("observation").value="";$("status").textContent="";render();}
$("file").onchange=e=>{const file=e.target.files[0];if(!file)return;if(!file.type.startsWith("video/")&&!/\.(mp4|mov|webm|m4v|ogv)$/i.test(file.name)){$("status").textContent=t("invalid");e.target.value="";return;}if(markers.length&&!confirm(t("discard"))){e.target.value="";return;}clear();url=URL.createObjectURL(file);v.src=url;e.target.value="";controls();};
v.addEventListener("loadedmetadata",()=>{v.playbackRate=Number($("speed").value);$("status").textContent=t("ready");controls();});
v.addEventListener("error",()=>{$("status").textContent=t("error");controls();});
$("speed").onchange=()=>{v.playbackRate=Number($("speed").value);};
function seek(time){if(ready()){v.pause();v.currentTime=Math.max(0,Math.min(v.duration,time));}}
$("prev").onclick=()=>seek(v.currentTime-.1);
$("next").onclick=()=>seek(v.currentTime+.1);
$("mark").onclick=()=>{if(!ready()||markers.length>=200)return;markers.push({seconds:Math.round(v.currentTime*1000)/1000,observation:$("observation").value.trim().slice(0,500)});markers.sort((a,b)=>a.seconds-b.seconds);$("observation").value="";render();};
$("close").onclick=()=>{if(!markers.length||confirm(t("discard")))clear();};
$("export").onclick=()=>{const blob=new Blob([JSON.stringify({version:1,kind:"acpa-video-feedback",markers},null,2)],{type:"application/json"});const href=URL.createObjectURL(blob),a=document.createElement("a");a.href=href;a.download="acpa-feedback.json";a.click();setTimeout(()=>URL.revokeObjectURL(href),1000);};
translate();
