// 경정청구 확인 계산기 (2026.10.22) — 2021~2025년분(경정청구 5년 안) 놓친 감면·공제 '가능성과 범위'만 보여 줌. 참고용
// 근거(연도별로 그 해 시행 법 기준, 근거자료\01. 조문 확인(2026-10-22).txt):
//  창업감면 조특법 6조①(청년 과밀억제권역 50%·그 외 100% / 일반 과밀 밖 50%), 6조⑥(생계형: 매출 2021년분 4,800만·2022~2025년분 8천만 이하, 과밀 50%·그 외 100%), 감면기간 최초 소득연도 + 4년
//  중소기업 특별세액감면 7조①(소기업: 도소매 10%, 그 외 감면업종 수도권 20%·지방 30%, 한도 1억)  · 6조와 7조는 같은 해 하나만(127조⑤)
//  고용: 2021~2022년 증가분 고용증대세액공제 29조의7(중소 청년 수도권 1,100만·지방 1,300만, 그 외 700만·770만)
//        2023~2025년 증가분 통합고용세액공제 29조의8(중소 청년 1,450만·1,550만, 그 외 850만·950만), 증가한 해 + 2년(중소), 직원 수는 매월 말 인원의 연평균(시행령 26조의8⑥)
//        감면(6·7조)과 고용공제는 함께 가능(127조④ 목록에 없음) — 단 2025년 이후 창업은 6조와 고용공제 중 하나(127조④ 단서, 부칙 20617)  · 추계 신고는 고용공제 배제(128조①)
//  근로자: 기본공제 1인 150만 + 경로우대(70세 이상) 100만, 월세 95조의2(2021년분 10·12% / 2022~2023년분 15·17% 한도 750만 총급여 7천 이하 / 2024~2025년분 15·17% 한도 1천만 총급여 8천 이하)
(function(){
  var YEARS=[2021,2022,2023,2024,2025];
  // 2026.10.22 태형: 통합고용을 받으면 고용증대는 못 받으므로(127조⑪) 통합고용(2023년 시행) 위주로만 — 2021~2022년 증가분은 0(계산 제외, 안내만)
  var JOB={2020:{y:[1100,1200],o:[700,770],nm:'고용증대세액공제'},   /* 2026.10.27 2020년 증가분의 2·3년 차(2021~2022년)용 — 2020년 시행 제29조의7① */
           2021:{y:[1100,1200],o:[700,770],nm:'고용증대세액공제'}   /* 2026.10.27 보수: 수도권 밖 청년 1,300만 단서(2021.12.28 개정)의 2021년분 적용 부칙을 확인 못 해 2021년은 종전 1,200만 */,2022:{y:[1100,1300],o:[700,770],nm:'고용증대세액공제'},   /* 2026.10.26 태형 '21년과 22년은 고용(증대)으로': 제29조의7(2021.12.28 개정 단서 — 2021~2022년 수도권 밖 청년 1,300만) */
          
           2023:{y:[1450,1550],o:[850,950],nm:'통합고용세액공제'},2024:{y:[1450,1550],o:[850,950],nm:'통합고용세액공제'},2025:{y:[1450,1550],o:[850,950],nm:'통합고용세액공제'}};
  var SMB={2021:4800,2022:8000,2023:8000,2024:8000,2025:8000};
  var RENT={2021:{cap:750,lim:'b',r:[12,10]},2022:{cap:750,lim:'b',r:[17,15]},2023:{cap:750,lim:'b',r:[17,15]},2024:{cap:1000,lim:'c',r:[17,15]},2025:{cap:1000,lim:'c',r:[17,15]}};
  // 총급여 구간별 '결정세액이 줄어드는 비율'(%) 대략 범위. 2026.10.23 독립검토: 산출세액이 작으면 근로소득세액공제(55%)도 같이 줄어 실제 효과는 45% 정도(a 하한 3%),
  // 2021~2022년은 과세표준 4,600만 원 초과 24% 구간이라 b·c 상한 24%
  function GRt(g,t){ return {a:[3,15], b: t<=2022?[15,24]:[15,15], c:[15,24], d:[24,35]}[g] || [15,15]; }
  var STARTUP_IND={online:1,food:1,beauty:1,mfg:1,build:1,it:1,retail:0,etc:-1};   // 6조③ 업종(1 해당, 0 아님, -1 확인 필요)
  var SPECIAL_IND={online:'w',retail:'w',mfg:'o',build:'o',it:'o',food:0,beauty:0,etc:-1}; // 7조: w 도소매 10%, o 그 외 감면업종

  function r0(n){return Math.round(n);}
  // 최저한세(조특법 제132조) 대략: 개인 = 사업소득 산출세액의 35%(3천만 원 초과분 45%), 법인(중소) = 과세표준의 7%.
  // 법인 과세표준은 납부세액에서 거꾸로 추정(2022년까지 10%·20%, 2023년부터 9%·19%). 납부세액을 산출세액으로 봄
  function minTax(kind,t,T){ if(T<=0) return 0;
    if(kind==='c'){ var r1=t<=2022?0.10:0.09, r2=t<=2022?0.20:0.19, X = T<=20000*r1 ? T/r1 : 20000+(T-20000*r1)/r2; return 0.07*X; }
    return 0.35*Math.min(T,3000)+0.45*Math.max(0,T-3000); }
  // 직원 수 연평균: max = 1월에 뽑은 것으로(연말 인원 그대로), min = 7월에 뽑은 것으로(늘어난 인원의 절반만 그 해에 잡힘) — 2026.10.26 태형 '범위는 하되 좁게'(12월 채용 극단값은 뺌)
  function avgSeries(end, prevEnd, low){
    var out={}, p=prevEnd;
    YEARS.forEach(function(t){ if(end[t]==null){out[t]=null;return;} var e=end[t]; out[t]=(low && e!==p)? p+(e-p)*0.5 : e; p=e; /* 2026.10.26 연중(7월) 기준은 채용뿐 아니라 퇴사도 7월로 봄 */ });
    return out;
  }
  function jobCredit(o, low, reg, ageOut, v){   // v=1: 고용증대(29세)·통합고용(34세) 청년 기준 차이를 보수적으로(2026.10.26) // reg: 0 수도권, 1 지방 / ageOut: 청년 등 인원 감소를 나이 초과 때문으로 볼지(추징 계산만, 시행령 제26조의8⑤)
    var tot={}, yth={}, endT={}, endY={}, res={};
    YEARS.forEach(function(t){ var r=o.rows[t]; if(!r) return; endY[t]=r.y||0; endT[t]=(r.y||0)+(r.o||0); res[t]=0; });
    var pt, py, noFirst=(o.first==='n' && o.open && o.open.y>=2021);   /* 2026.10.27 승계·법인전환이면 첫해 비교 대상이 전 사업자 인원 → 보수적으로 개업 연도 증가분 제외 */ if(o.base && !noFirst){ pt=o.base.y+o.base.o; py=o.base.y; } else { var f0=YEARS.filter(function(t){return endT[t]!=null;})[0]; pt=f0?endT[f0]:0; py=f0?endY[f0]:0; }   // 2020년 말 인원을 모르면 2021년 증가분은 계산 안 함
    // 2026.10.26 태형 '연도별 평균 직원 수를 입력하라고 해도 될 듯': 기본은 연평균 인원 그대로 / 12월 말 인원으로 넣었다고 체크하면 채용한 달(1월·12월)로 범위
    if(o.cntEnd){ tot=avgSeries(endT, pt, low); yth=avgSeries(endY, py, low); } else { tot=endT; yth=endY; }
    var prevT=pt, prevY=py, firsts=[];
    // 2026.10.27 태형 ㄱㄱ: 2019·2020년 말 인원을 알면 2020년 증가분(고용증대)의 2021~2022년 공제(2·3년 차)도 계산. 1년 차를 경정청구 기간 경과로 못 받았어도 2·3년 차는 가능(서면-2024-법규법인-2296)
    if(o.base && o.base0 && !(o.first==='n' && o.open && o.open.y===2020)){   /* 2026.10.27 재검토: 2020년 개업 승계·전환이면 2020년 증가분 제외 */ var p0T=o.base0.y+o.base0.o, p0Y=o.base0.y, e0T=o.base.y+o.base.o, e0Y=o.base.y;
      var a0T=(low && o.cntEnd && e0T!==p0T)? p0T+(e0T-p0T)*0.5 : e0T, a0Y=(low && o.cntEnd && e0Y!==p0Y)? p0Y+(e0Y-p0Y)*0.5 : e0Y;
      tot[2020]=a0T; yth[2020]=a0Y; prevT=a0T; prevY=a0Y;
      var inc0=a0T-p0T; if(inc0>0.0001){ var iy0=Math.min(Math.max(0,a0Y-p0Y),inc0), io0=inc0-iy0, J0=JOB[2020]; firsts.push({t:2020, lvl:a0T, ylvl:a0Y, iy:iy0, io:io0, J:J0, amt:iy0*J0.y[reg]+io0*J0.o[reg]}); } }
    YEARS.forEach(function(t){
      if(tot[t]==null) return;
      var inc=tot[t]-prevT;
      if(inc>0.0001){ var iy=Math.min(Math.max(0,yth[t]-((v===1&&t===2023&&o.rows[2022])?prevT:prevY)),inc), io=inc-iy, J=JOB[t];   /* v=1: 2022년 '그 외'가 모두 30~34세였다고 보고 2023년 청년 증가를 작게 */
        firsts.push({t:t, lvl:tot[t], ylvl:yth[t], iy:iy, io:io, J:J, amt:iy*J.y[reg]+io*J.o[reg]}); }
      prevT=tot[t]; prevY=yth[t];
    });
    // 2026.10.23 독립검토: 제29조의8제2항 — 최초 공제 연도부터 2년 안에 전체 인원이 줄면 그 해부터 적용 안 하고 이미 공제받은 세액도 납부 → 그 증가분 몫은 0으로.
    // 청년등 인원만 줄면 그 해부터 청년등 단가를 적용 안 하고 차액을 납부 → 그 증가분의 청년등 몫을 '그 외' 단가로.
    // 2026.10.23 재검토: 줄어든 해부터는 공제 없음(청년등만 줄면 그 해부터 그 외 단가). 이미 받은 공제의 추징액(시행령 제26조의8 산식)은 계산하지 않고 '확인 필요'로 넘김
    // 2026.10.26 태형 '로직이 복잡해져도 반영': 추징액(시행령 제26조의8④, 2023·2024년 최초 공제분 기준)까지 계산
    //  · 전체 인원이 줄면 그 해부터 공제 없음 + 추징 / 청년 등만 줄면 그 해부터 그 외 단가 + 추징(차액)
    //  · 추징 계산 때는 최초 공제 연도에 청년이었던 사람을 이후에도 청년으로 봄(⑤) → ageOut이면 청년 등 감소를 나이 초과로 보고 추징에서 뺌
    //  · 한도: 1년 안(1호)은 최초 연도 공제액, 2년 안(2호)은 직전 2년 공제액 합계에서 1호 금액을 뺀 것. 최저한세로 이월된 부분은 따로 보지 않음(대략)
    res.claw={}; YEARS.forEach(function(t){ res.claw[t]=0; });
    firsts.forEach(function(f){ var Py=f.J.y[reg], Po=f.J.o[reg], stop=false, yOnly=false, cred={}, k1=0;
      for(var s=f.t; s<=f.t+2 && s<=2025; s++){ if(tot[s]==null) break;
        if(s===f.t){ cred[s]=f.amt; if(s in res) res[s]+=f.amt; continue; }   /* 2020년 1년 차는 계산 기간 밖(추징 한도 계산에는 받은 것으로 봄 — 보수적) */
        var ythC = ageOut ? Math.max(yth[s], Math.min(f.ylvl, tot[s])) : yth[s];
        var D=Math.max(0,f.lvl-tot[s]), Yd=Math.max(0,f.ylvl-ythC), Od=Math.max(0,(f.lvl-f.ylvl)-(tot[s]-ythC));
        if(D>0.0001){ stop=true; res.__drop=true; res.__tdrop=true; }
        if(yth[s]+0.0001<f.ylvl){ yOnly=true; res.__drop=true; res.__ydrop=true; }
        var base=0;
        if(D>0.0001) base = Yd>=D ? (Math.min(Yd,f.iy)-D)*(Py-Po) + D*Py : Math.min(Yd,D)*Py + Math.min(Od,D)*Po;
        else if(Yd>0.0001) base = Math.min(Yd,f.iy)*(Py-Po);
        base=Math.max(0,base);
        var k=0;
        if(s===f.t+1){ k=Math.min(base, cred[f.t]||0); k1=k; }
        else { /* 2026.10.26 태형 '보수적으로': 2호 횟수는 문언대로 공제받은 해를 모두 셈(그 외 단가로 받은 해 포함) — 추징이 더 크게 나오는 쪽 */ var n=((cred[f.t]||0)>0?1:0)+((cred[f.t+1]||0)>0?1:0); k=Math.min(Math.max(0,base*n-k1), (cred[f.t]||0)+(cred[f.t+1]||0)); }
        if(k>0.0001){ res.claw[s]+=k; res.__claw=true; }
        if(v===1 && f.t<=2022 && s>=2023) yOnly=true;   /* 고용증대 증가분은 2023년부터 29세 기준 청년 수를 알 수 없어, 최소 쪽은 청년 추가 공제를 빼고 계산 */
        cred[s] = stop ? 0 : (yOnly ? (ageOut ? (f.iy+f.io) : f.io)*Po : f.amt);   /* 2026.10.27 재검토: 나이 초과면 그 외 단가로 계속(서면-2024-소득-4000), 퇴사 등이면 제1항제1호 미적용 문언대로 그 외 증가분만 */
        res[s]+=cred[s];
      } });
    return res;
  }
  function biz(o){ // o: {kind:'p'|'c', open:{y,m}, ind, reg:'over'|'metro'|'local'|'unk', age, mil, first:'y'|'n'|'u', book:'book'|'est'|'u', got:'n'|'y'|'u', base:{y,o}, rows:{t:{rev,tax,y,o}}}
    var out={years:{}, notes:[], items:{}}, Y0=o.open.y, SEL=o.sel||{st:1,sp:1,jb:1};   // 2026.10.23 항목 선택형: 고른 항목만 계산
    // 2026.10.23 백테스트: '만 나이'는 생일에 따라 최대 11개월 차이 → 병역을 빼면 34세 경계에서 갈릴 수 있음(36세·21개월 등). 갈리면 두 경우 모두 계산해 범위로
    var ageLo = o.age>0 ? o.age - Math.min(o.mil||0,72)/12 : 99, ageHi = ageLo + 11/12;
    var youthSure = ageHi < 35, youthMaybe = !youthSure && ageLo < 35;
    var youth = youthSure;
    var stInd=STARTUP_IND[o.ind], spInd=SPECIAL_IND[o.ind];
    var regs = o.reg==='unk' ? ['over','local'] : [o.reg];
    // 2026.10.23 백테스트: 2018.5.29 전 창업은 종전 규정(부칙 제15623호 제4조) — 과밀억제권역 밖만 50%(청년 75%는 처음 3년뿐이라 2021~2022년엔 50%), 생계형 없음
    var oldReg = Y0<2018 || (Y0===2018 && (o.open.m||1)<=5);
    if(oldReg && (o.ind==='online'||o.ind==='beauty')) stInd=0;   // 2018.5.29 전 업종 목록엔 통신판매업·이용미용업 없음(2018.5.29 개정으로 추가)
    // 감면기간: 처음 소득이 난 해 + 4년(제6조제1항). 개업 후 5년째 해까지 소득이 없으면 그 해부터
    var FI = Math.min(o.firstInc||Y0, Y0+((o.open.m||1)>1?5:4)); if(FI<Y0) FI=Y0;
    var annMode=true;
    function stRate(rg, rev, t){ // 창업감면 비율(%)
      if(oldReg) return rg==='over'?0:50;
      if(youth) return rg==='over'?50:100;
      if(rev!=null){ var rv = (t===Y0 && o.open.m>1 && annMode) ? rev*12/(13-o.open.m) : rev;   // 첫해는 1년으로 환산한 수입금액(제6조제6항)
        if(rv<=SMB[t]) return rg==='over'?50:100; }   // 생계형
      return rg==='over'?0:50;
    }
    function spRate(rg,rev){ if((rev||0)>1200000) return rg==='local' ? (spInd==='w'?5:(spInd==='o'?15:0)) : 0;   /* 2026.10.27 재검토(2차): 매출 120억 원 초과는 소기업이 아닐 가능성이 커 최대도 중기업 감면율(보수) */ if(spInd==='w') return 10; if(spInd==='o') return (rg==='local')?30:20; return 0; }
    // 경우를 나눠 계산: 지역(모르면 과밀억제권역·지방 둘 다) × 직원을 뽑은 달(1월·12월). 결과는 그중 가장 작은 경우 ~ 가장 큰 경우
    // 6조와 7조는 같은 해 큰 쪽 하나만(127조⑤), 추계 신고면 고용공제 배제(128조①), 2025년 이후 창업은 창업감면과 고용공제 중 하나(127조④ 단서)
    var combos=[];
    // 2026.10.27 재검토(보수): 모름·일부로 고른 입력은 '나쁜 쪽'도 함께 계산해 범위 최소에 반영
    //  최초 창업 '모름'(고용) → 승계로 보고 개업 연도 증가분 제외 / 신고 방식 '모름' → 고용 0 / 기한 후 '일부·모름' → 6·7조 0 / 매출 10억 초과 → 소기업 아닐 수 있어 7조 0
    var anyBig = Object.keys(o.rows).some(function(k){return (o.rows[k].rev||0)>100000});
    var anyHuge = Object.keys(o.rows).some(function(k){return (o.rows[k].rev||0)>4000000});   /* 2026.10.27 재검토(2차): 매출 400억 원 초과는 중소기업이 아닐 수도 있어 창업감면 최소 0 */
    var PESS = ((SEL.jb && (o.first==='u' || o.book==='u')) || ((SEL.st||SEL.sp) && (o.late==='part'||o.late==='u')) || (SEL.sp && anyBig) || (SEL.st && anyHuge)) ? [false,true] : [false];
    // 7조 한도: 직원 수가 직전 해보다 줄면 1억 원에서 1명당 500만 원씩 줄어듦(제7조제1항제3호) — 직원 수를 받은 경우에만
    var spCap={}; (function(){ var p=o.base?o.base.y+o.base.o:null; YEARS.forEach(function(t){ var r=o.rows[t]; if(!r) return; var v=(r.y||0)+(r.o||0); spCap[t]=(SEL.jb && p!=null && v<p)? Math.max(0,10000-500*(p-v)) : 10000; p=v; }); })();
    var anns = (o.kind==='p' && o.open.m>1 && Y0>=2021) ? [true,false] : [true], stByAnn={};
    anns.forEach(function(am){ annMode=am;
    (youthMaybe?[false,true]:[youthSure]).forEach(function(yv){ youth=yv;
    regs.forEach(function(rg){ var jr=(rg==='local')?1:0;
      var Js=[]; PESS.forEach(function(ps){ var oo=(ps && o.first==='u')? Object.assign({},o,{first:'n'}) : o;
        ((Y0<=2022 && o.rows[2023])?[0,1]:[0]).forEach(function(v){ var a=jobCredit(oo,false,jr,false,v), b2=jobCredit(oo,true,jr,false,v); a.__ps=b2.__ps=ps; Js.push(a,b2); if(a.__ydrop||b2.__ydrop){ var c1=jobCredit(oo,false,jr,true,v), c2=jobCredit(oo,true,jr,true,v); c1.__ps=c2.__ps=ps; Js.push(c1,c2); } }); });   // 2026.10.26 청년 등 감소가 나이 때문인지 모르면 두 경우 모두
      Js.forEach(function(J){
        /* 2026.10.27 재검토(2차): 경정청구는 고용 공제를 '신청하지 않을' 수도 있음 → 추징이 더 커서 손해인 경우는 고용 공제 없이 계산한 쪽을 씀 */
        function runY(useJ){ var a={st:0,sp:0,jb:0,cap:0,stRaw:0,y:{}};
        YEARS.forEach(function(t){ var r=o.rows[t]; if(!r) return; var T=Math.max(0,r.tax||0), inWin=t>=FI&&t<=FI+4;
          var lateX = J.__ps && (o.late==='part'||o.late==='u');
          var s=(SEL.st && inWin && stInd===1 && o.first!=='n' && o.late!=='late' && !lateX)? T*stRate(rg,r.rev,t)/100 : 0;   // 기한 후 신고면 6·7조 배제(128조②)
          var p=(SEL.sp && (spInd==='w'||spInd==='o') && o.late!=='late' && !lateX)? Math.min(T*spRate(rg,r.rev)/100,spCap[t]) : 0;
          if(J.__ps && (r.rev||0)>100000) p=0; if(J.__ps && (r.rev||0)>4000000) s=0; a.stRaw+=s;
          if(o.gotI && o.gotI.st && inWin) p=0;   /* 2026.10.27 재검토: 창업감면을 이미 받은 기간에는 7조를 같은 해에 못 받음(제127조⑤) */
          var j0=(SEL.jb&&useJ)?(J[t]||0):0; if(o.book==='est' || (J.__ps && o.book==='u')) j0=0;
          var k0=(SEL.jb && useJ && o.book!=='est' && !(J.__ps && o.book==='u'))?(J.claw[t]||0):0;
          if(Y0>=2025 && o.gotI && o.gotI.st){ j0=0; k0=0; }   /* 2026.10.27 재검토: 2025년 이후 창업으로 창업감면을 받았으면 고용 공제 동시 적용 안 됨(제127조④ 단서) */   // 2026.10.26 그 해에 다시 내야 하는 공제(추징)
          var lim=T-minTax(o.kind,t,T);                                 // 최저한세(제132조): 이 한도까지만 감면·공제
          var full = s>=p && s>0 && stRate(rg,r.rev,t)===100;          // 창업감면 100%인 해는 최저한세 적용 제외(제132조 각 항 제4호 가목)
          function capd(g,j){ return full ? Math.min(g+j,T) : Math.min(g+j,lim,T); }
          var g,j,sum;
          if(Y0>=2025 && s>0){                                          // 2025년 이후 창업: 창업감면과 고용공제 중 하나(제127조④ 단서) → 유리한 쪽
            var A=capd(s,0), B=capd(p,j0), Bn=B-0.2*Math.max(0,B-Math.min(p,B));   /* 2026.10.27 재검토(2차): 고용 공제 쪽은 농어촌특별세(20%)를 뺀 금액으로 비교 */
            if(A>=Bn){ g=s; j=0; sum=A; a.st+=s; } else { g=p; j=j0; sum=B; if(p>0) a.sp+=p; }
          } else { g=Math.max(s,p); if(s>=p) a.st+=s; else a.sp+=p; j=j0; sum=capd(g,j); }
          var nt=0.2*Math.max(0, sum-Math.min(g,sum));   /* 2026.10.27 보수: 실제 적용된 고용 공제액의 20% 농어촌특별세를 환급 예상액에서 뺌(6·7조 감면은 비과세 — 농특세법 제4조제3호) */
          sum-=k0+nt; a.jb+=j-k0; a.cap+=sum; a.y[t]={g:g,j:j,k:k0,nt:nt,sum:sum+0,over:g+j>sum+k0+nt+0.0001,mt:!full && g+j>lim && lim<T};
        }); return a; }
        var a=runY(true); if(SEL.jb){ var a0=runY(false); if(a0.cap>a.cap+0.0001){ a0.jbSkip=true; a=a0; } }
        combos.push(a); stByAnn[am]=Math.max(stByAnn[am]||0,a.st); });
    }); }); });
    youth=youthSure; annMode=true;
    var annAmb = anns.length>1 && Math.abs((stByAnn[true]||0)-(stByAnn[false]||0))>0.5;
    var jbTDrop = SEL.jb && regs.some(function(rg){ return jobCredit(o,false,rg==='local'?1:0).__tdrop || jobCredit(o,true,rg==='local'?1:0).__tdrop; });   // 2026.10.26 전체 인원이 줄어든 경우
    var jbYDrop = SEL.jb && regs.some(function(rg){ return jobCredit(o,false,rg==='local'?1:0).__ydrop || jobCredit(o,true,rg==='local'?1:0).__ydrop; });   // 2026.10.26 청년 등 인원만 줄어든 경우
    var jbDrop = SEL.jb && regs.some(function(rg){ return jobCredit(o,false,rg==='local'?1:0).__drop || jobCredit(o,true,rg==='local'?1:0).__drop; });
    function mm(f){ var v=combos.map(f); return [Math.min.apply(null,v),Math.max.apply(null,v)]; }
    YEARS.forEach(function(t){ var r=o.rows[t]; if(!r) return;
      out.years[t]={tax:r.tax||0, red:mm(function(a){return a.y[t].g}), job:mm(function(a){return a.y[t].j}), claw:mm(function(a){return a.y[t].k}), nt:mm(function(a){return a.y[t].nt}), sum:mm(function(a){return a.y[t].sum}), over:combos.some(function(a){return a.y[t].over})}; });
    var stR=mm(function(a){return a.st}), spR=mm(function(a){return a.sp}), jbR=mm(function(a){return a.jb}), capR=mm(function(a){return a.cap});
    // 고용공제 최대는 추계·2025 창업 제한 전 금액으로도 보여 줌(확인 필요 표시용)
    var jbRaw=!SEL.jb?0:(function(){ var v=0; regs.forEach(function(rg){ var J=jobCredit(o,false,rg==='local'?1:0); var x=0; YEARS.forEach(function(t){ x+=J[t]||0; }); v=Math.max(v,x); }); return v; })();
    var stRawMax=Math.max.apply(null,combos.map(function(a){return a.stRaw})); out.jbSkip=combos.some(function(a){return a.jbSkip}); var jbSkipAll=SEL.jb && combos.every(function(a){return a.jbSkip});
    var st={min:stR[0],max:stR[1],any:stR[1]>0}, sp={min:spR[0],max:spR[1],any:spR[1]>0}, jb={min:jbR[0],max:jbR[1]}, cap={min:capR[0],max:capR[1]};
    // 안내용 표시: 2021~2022년 증가(고용증대)와 2023년 이후 증가(통합고용)가 함께 있는지, 2020년 이전 증가분이 이어질 수 있는지
    (function(){ var p=o.base?o.base.y+o.base.o:1e9, e=false, l=false; YEARS.forEach(function(t){ var r=o.rows[t]; if(!r) return; var v=(r.y||0)+(r.o||0); if(v>p){ if(t<=2022) e=true; else l=true; } p=v; });
      out.mixJob = e&&l; out.preJob = Y0<=2020 && !!o.base && (o.base.y+o.base.o)>0; out.noBase = Y0<=2020 && !o.base; out.noBase0 = Y0<=2019 && !!o.base && !o.base0; out.pre19 = Y0<=2019; out.firstN = !!SEL.jb && o.first==='n' && Y0>=2020; out.firstU = !!SEL.jb && o.first==='u' && Y0>=2020; out.bookU = !!SEL.jb && o.book==='u'; out.etc = o.ind==='etc'; out.firstQ = !!SEL.jb && !SEL.st && Y0>=2021; out.socIns = Y0<=2022; })();
    out.youth=youth; out.youthMaybe=youthMaybe; out.oldReg=oldReg; out.oldInd=oldReg&&(o.ind==='online'||o.ind==='beauty'); out.mt=combos.some(function(a){return Object.keys(a.y).some(function(t){return a.y[t].mt})});
    var lateNo={lv:'no', why:'기한 후 신고한 해는 창업감면·중소기업 특별세액감면을 받을 수 없습니다(조세특례제한법 제128조제2항).'};
    out.items.st = o.late==='late' ? lateNo : stInd===0||o.first==='n' ? {lv:'no', why: stInd===0?((oldReg&&(o.ind==='online'||o.ind==='beauty'))?'2018년 5월 29일 전 창업 당시 법에는 통신판매업·미용업이 창업감면 대상 업종에 없었습니다':'일반 소매업 등은 창업감면 대상 업종이 아닙니다'):'같은 업종을 전에 했거나 이어받은 경우(폐업 후 같은 업종 재개, 개인사업자의 법인 전환 등)는 창업으로 보지 않아 창업감면 대상이 아닙니다'}
                 : stInd===-1 ? {lv:'chk', why:'업종에 따라 창업감면 대상일 수도 있어 금액은 상담에서 확인합니다', min:0, max:0}
                 : (!st.any && Y0>=2025 && stRawMax>0.5) ? {lv:'chk', why:'2025년 이후 창업은 창업감면과 고용 공제 중 하나만 받을 수 있습니다. 해마다 유리한 쪽으로 계산했더니 고용 공제(중소기업 특별세액감면 포함) 쪽이 더 커서 창업감면은 0원으로 잡았습니다(창업감면만 받으면 최대 약 '+Math.round(stRawMax).toLocaleString('ko-KR')+'만 원). 어느 쪽이 나은지는 세무사 검토가 필요합니다.', min:0, max:0}
                 : !st.any ? {lv:(FI+4<2021&&!o.firstInc)?'chk':'no', why:(FI+4<2021?(o.firstInc?'처음 소득이 난 해부터 5년(감면 기간)이 2021년 전에 끝나 이번 확인 기간(2021~2025년)에 들지 않습니다':'개업한 해부터 5년이 2021년 전에 끝납니다. 다만 감면 기간은 처음 이익(소득)이 난 해부터 세므로, 초기에 적자였다면 상담에서 확인합니다'):
                     Object.keys(o.rows).every(function(k){return !(o.rows[k].tax>0)})?'입력하신 연도에 납부세액이 없어 돌려받을 세금이 없습니다':
                     oldReg?'2018년 5월 29일 전 창업은 그때 법이 적용돼 과밀억제권역에서 창업한 경우 감면 대상이 아닙니다':
                     '청년이 아니고 매출이 생계형 기준을 넘는 해에, 과밀억제권역에서 창업한 경우는 감면율이 0%입니다')}
                 : {lv:(stInd===-1||o.first==='u'||youthMaybe)?'chk':'hi', min:st.min, max:st.max, youth:youth};
    out.items.sp = o.late==='late' ? lateNo : (spInd===0)? {lv:'no', why:'음식점·미용실은 중소기업 특별세액감면 대상 업종이 아닙니다'}
                 : (spInd===-1)? {lv:'chk', why:'업종에 따라 대상이 될 수도 있습니다', min:0, max:0}
                 : (sp.max<=0? {lv:'no', why: Object.keys(o.rows).every(function(k){return !(o.rows[k].tax>0)})?'입력하신 연도에 납부세액이 없어 돌려받을 세금이 없습니다':(o.gotI&&o.gotI.st)?'창업감면을 이미 받으셨다고 고르셔서, 창업감면 기간(5년) 안의 해는 중소기업 특별세액감면을 빼고 계산했습니다(같은 해에는 하나만 받을 수 있습니다).':'창업감면이 더 커서 그해에는 창업감면으로 계산했습니다(같은 해에는 하나만 적용됩니다).'} : {lv:'hi', min:sp.min, max:sp.max});
    out.items.jb = jbSkipAll ? {lv:'chk', why:'직원이 줄어 다시 내야 할 공제(추징)가 공제액보다 커서, 고용 공제는 신청하지 않는 쪽으로 계산했습니다(0원). 세무사 검토가 필요합니다.', min:0, max:0}
                 : (jb.max<=0 && jbRaw>0 && o.book==='est') ? {lv:'chk', why:'장부 없이(추계) 신고한 해는 고용 공제를 받을 수 없어 0원으로 계산했습니다. 첫해를 추계로 신고했다면 그 뒤 2·3년 차 공제도 받을 수 없습니다. 장부로 신고했는지는 상담에서 확인합니다.', min:0, max:0}
                 : (jb.max<=0 && jbRaw>0 && Y0>=2025 && o.gotI && o.gotI.st) ? {lv:'chk', why:'2025년 이후 창업으로 창업감면을 받으셨다면 고용 공제는 같은 해에 함께 받을 수 없어 0원으로 계산했습니다(조세특례제한법 제127조제4항 단서).', min:0, max:0}
                 : (jb.max<=0 && jbRaw>0) ? {lv:'chk', why:'2025년 이후 창업은 창업감면과 통합고용세액공제 중 하나만 받을 수 있어, 해마다 더 유리한 쪽으로 계산했더니 창업감면이 더 컸습니다(통합고용만 받으면 최대 '+Math.round(jbRaw).toLocaleString('ko-KR')+'만 원).', min:0, max:0}
                 : jb.max<=0 ? {lv:'no', why:'2021~2025년에 공제받을 수 있는 상시근로자 증가분이 없습니다.'+(out.noBase0?' 2019년 말 직원 수를 비워 두셔서 2020년에 늘어난 직원 몫은 계산하지 않았습니다.':'')+(out.noBase?' 2020년 말 직원 수를 비워 두셔서 2021년에 늘어난 직원 몫은 계산하지 않았습니다.':'')}
                 : {lv:(o.book==='est'||o.book==='u')?'chk':'hi', min:jb.min, max:jb.max, est:o.book==='est'};
    // 2026.10.23 재검토: 판단이 갈리는 경우는 계산을 더 하지 않고 '확인 필요'로 넘김
    out.annAmb=annAmb; out.jbDrop=jbDrop; out.jbTDrop=jbTDrop; out.jbYDrop=jbYDrop; out.corpYouth = o.kind==='c' && (youthSure||youthMaybe);
    if(SEL.st && out.items.st.lv==='hi' && (annAmb || out.corpYouth || oldReg)) out.items.st.lv='chk';
    if(out.items.jb.lv==='hi' && (jbDrop || out.firstU || out.etc)) out.items.jb.lv='chk';   /* 2026.10.27 재검토: 최초 창업 모름·그 밖의 업종도 확인 필요 */
    if(!SEL.st) out.items.st={lv:'off'}; if(!SEL.sp) out.items.sp={lv:'off'}; if(!SEL.jb) out.items.jb={lv:'off'};
    out.total=[cap.min,cap.max];
    return out;
  }
  function worker(o){ // o.rows[t] = {g:'a'|'b'|'c'|'d', paid:결정세액(만원,0=모름), par:빠뜨린 부모 수, old:그중 70세 이상, rent:월세 월액(만원)}
    var out={years:{}, dep:[0,0], rent:[0,0], sme:[0,0], total:[0,0]};
    YEARS.forEach(function(t){
      var r=o.rows[t]; if(!r) return; var g=GRt(r.g,t);
      var WS=o.sel||{dep:1,rent:1}; var base=WS.dep?(r.par||0)*150+(Math.min(r.old||0,r.par||0))*100:0;
      var d0=base*g[0]/100, d1=base*g[1]/100;
      /* 2026.11.02 보수 수정: 중소기업 취업자 감면을 받는 해는 세금 대부분이 감면돼 부양가족(소득공제) 효과가 그만큼 줄어듦 → 감면율×감면 달 비율만큼 낮춤(최대 감면율 기준) */
      var SI=WS.sme? smeYear(o.sme,t,r.paid) : {v:[0,0],sh:0}; if(SI.sh>0){ d0*=(1-SI.sh); d1*=(1-SI.sh); }
      var R=RENT[t], okRent = WS.rent && r.rent>0 && (r.g==='a'||r.g==='b'||(R.lim==='c'&&r.g==='c'));
      var rr = okRent ? Math.min(r.rent*12,R.cap)*(r.g==='a'?R.r[0]:R.r[1])/100 : 0;
      if(r.paid>=0){ d0=Math.min(d0,r.paid); d1=Math.min(d1,r.paid); } else d0=0;   /* 2026.10.27 재검토(2차): 결정세액을 모르면 0원일 수도 있어 최소 0 */   /* 2026.10.27 재검토: 0원도 한도(빈칸=-1=모름) */   // 납부세액(결정세액)을 넣었으면 그 한도 안에서
      // 2026.10.23 독립검토: 월세 공제를 받으면 표준세액공제 13만 원을 못 받음(소득세법 제59조의4제9항제1호) → 다른 특별공제가 없던 분은 13만 원 덜 돌려받음
      var rl=Math.max(0,rr-13), rh=rr;
      var lo=d0+rl, hi=d1+rh; if(r.paid>=0){ lo=Math.min(lo,r.paid); hi=Math.min(hi,r.paid); } else lo=0;
      var rentLo = r.paid>=0 ? Math.max(0,Math.min(rl, r.paid-d1)) : 0, rentHi = r.paid>=0 ? Math.max(0,Math.min(rh, r.paid-d0)) : rh;   /* 2026.10.27 재검토(2차): 결정세액 한도가 걸리면 최소는 부양가족 공제가 크게 잡힌 경우 기준 — 범위가 뒤집히지 않게 */
      /* 2026.11.02 중소기업 취업자 소득세 감면(조특법 제30조): 결정세액 × 감면율(청년 90%·그 외 70%) × 아직 안 받은 감면기간 비율, 연 한도 2022년분까지 150만·2023년분부터 200만. 결정세액 기준이라 보수적 */
      var sm=SI.v.slice();
      if(sm[1]>0){ var sLo=r.paid>=0? Math.max(0,Math.min(sm[0], r.paid-hi)) : 0, sHi=r.paid>=0? Math.max(0,Math.min(sm[1], r.paid-lo)) : sm[1];   // 결정세액 한도 안에서 — 부양가족·월세와 합쳐 넘지 않게
        lo+=sLo; hi+=sHi; if(r.paid>=0){ lo=Math.min(lo,r.paid); hi=Math.min(hi,r.paid); } sm=[sLo,sHi]; }
      out.years[t]={dep:[d0,d1], rent:[rentLo,rentHi], sme:sm, smeSh:SI.sh>0&&base>0, rentNo: r.rent>0 && !okRent, sum:[lo,hi], unk:r.paid<0, capped:r.paid>=0 && (base*g[1]/100+rr>r.paid)};
      out.dep[0]+=d0; out.dep[1]+=d1; out.rent[0]+=rentLo; out.rent[1]+=rentHi; out.sme[0]+=sm[0]; out.sme[1]+=sm[1]; out.total[0]+=lo; out.total[1]+=hi;
    });
    return out;
  }
  // s={kind:'y'|'o'|'u', ind:'ok'|'no'|'u', y,m:취업 연월, req:'never'|'mid'|'unk', ry:감면 신청 시작 연도, quit} → {v:[최소,최대](만원), sh:부양가족 공제를 줄일 비율}
  // 2026.11.02 보수 수정(태형 '부풀리면 안 된다'): ① 한도에 걸리는 해는 근로소득세액공제가 같이 줄어드는 몫(시행령 27⑨)을 빼고 — 근로소득세액공제를 최대 74만 원으로 보고 낮게
  //   ② 대상·업종을 모르면 최소 0 ③ 회사에 신청한 해는 그해 연말정산 때 1년 전체에 반영됐을 수 있어 그해부터 이미 받은 것으로 ④ 대상 업종이 아니면 0
  function smeYear(s,t,paid){ var Z={v:[0,0],sh:0}; if(!s||!s.y||s.ind==='no') return Z;
    var st=s.y*12+(s.m-1), ys=t*12, ye=t*12+11, cap=t<=2022?150:200;
    var K=s.kind==='y'?[[90,60]]:s.kind==='o'?[[70,36]]:[[70,36],[90,60]];   // 감면기간: 취업일부터 5년(3년)이 되는 날이 속하는 달까지
    var sh=0, v=K.map(function(k){ var end=st+k[1], a=Math.max(st,ys), b=Math.min(end,ye), el=Math.max(0,b-a+1); if(!el) return 0;
      var wk=ye-a+1; sh=Math.max(sh, k[0]/100*el/wk);
      if(s.req==='mid'&&s.ry&&t>=s.ry) return 0;   // 신청한 해부터는 이미 받음
      var f=el/wk, capR = paid>=0 ? cap*f*paid/(paid+74) : cap*f;
      return Math.min((paid>=0?paid:Infinity)*k[0]/100*f, capR); });
    var lo=Math.min.apply(null,v), hi=Math.max.apply(null,v); if(s.req==='unk'||s.kind==='u'||s.ind==='u'||paid<0) lo=0; return {v:[lo,hi], sh:sh}; }
  window.__claim={biz:biz, worker:worker, jobCredit:jobCredit, smeYear:smeYear, YEARS:YEARS};
})();

// ---------- 화면 ----------
(function(){
  var $=function(id){return document.getElementById(id)}; if(!$('cr')) return;
  var C=window.__claim, YEARS=C.YEARS, LEAD={}; try{ LEAD=JSON.parse($('cr').getAttribute('data-lead'))||{}; }catch(e){}
  var sentKey='', sending='', lastMemo='';
  function n(v){ v=String(v==null?'':v).replace(/[^0-9.]/g,''); return v===''?null:Number(v); }
  function man(x){ x=Math.round(x); if(x>=10000){ var e=Math.floor(x/10000), m=x%10000; return e+'억'+(m?' '+m.toLocaleString('ko-KR')+'만':'')+' 원'; } return x.toLocaleString('ko-KR')+'만 원'; }
  function rng(a,b){ a=Math.round(a); b=Math.round(b); if(b<=0) return '-'; return a===b? '약 '+man(b) : '약 '+(a>0?man(a):'0원')+' ~ '+man(b); }
  function rngN(a,b){ a=Math.round(a); b=Math.round(b); return a===b? '(-)'+man(b) : (a>0?'(-)'+man(a)+' ~ (-)'+man(b):'최대 (-)'+man(b)); }   // 2026.10.26 추징액 표시
function rngS(a,b){ a=Math.round(a); b=Math.round(b); if(a>=0) return rng(a,b); var f=function(x){ return x<0?'(-)'+man(-x):(x>0?man(x):'0원'); }; return a===b? '약 '+f(a) : '약 '+f(a)+' ~ '+f(b); }   // 음수(추징이 더 큰 해)는 (-)로
function won(m){ return Math.round((m||0)*10000).toLocaleString('ko-KR')+'원'; }
  // 원 단위 입력 칸: 쉼표 넣고, 옆에 '7,000만 원'처럼 읽기 쉬운 표시
  function comma(e){ var t=e.target; if(!t.matches||!t.matches('input[data-k="rev"],input[data-k="tax"],input[data-k="paid"],input[data-k="rent"]')) return;
    var v=t.value.replace(/[^0-9]/g,'').replace(/^0+(?=\d)/,'').slice(0,13); t.value=v?Number(v).toLocaleString('ko-KR'):''; t.title=v?korW(Number(v)):'';
    var hint=t.closest('table') && t.closest('table').id==='crWorkTbl' ? $('crAmtHint2') : $('crAmtHint');
    if(hint){ var x=Number(v||0); hint.textContent = !v ? '' : (x>0 && x<10000 ? '⚠ 원 단위로 입력해 주세요(예: 7천만 원 → 70,000,000). 입력한 값: '+korW(x) : '입력한 금액: '+korW(x)); hint.style.color = x>0&&x<10000 ? '#c62828' : ''; } }
  document.addEventListener('input',function(e){ var t=e.target; if(t.matches&&t.matches('#crBizTbl input[data-k="y"],#crBizTbl input[data-k="o"],#crAge,#crMil')){ var v=t.value.replace(/[^0-9.]/g,''); if(v!==t.value) t.value=v; } },true);
  function korW(x){ var e=Math.floor(x/1e8), m=Math.floor((x%1e8)/1e4), r=x%1e4, o=[]; if(e) o.push(e.toLocaleString('ko-KR')+'억'); if(m) o.push(m.toLocaleString('ko-KR')+'만'); if(r&&!e) o.push(r.toLocaleString('ko-KR')); return (o.join(' ')||'0')+' 원'; }
  document.addEventListener('input',comma,true);
  function checked(name){ return [].map.call(document.querySelectorAll('input[name='+name+']:checked'),function(i){return i.value}); }
  function txt(id){ var s=$(id); return s.selectedOptions&&s.selectedOptions[0]?s.selectedOptions[0].text:s.value; }
  // 1) 안내 확인
  function lock(){ var ok=$('agree').checked; $('crInfo').disabled=!ok; $('crInfo').style.opacity=ok?'':'.45'; $('lockMsg').hidden=ok; info(); }
  $('agree').addEventListener('change',lock);
  // 2) 기본 정보
  function infoOk(){ var nm=$('crName').value.trim(), ph=$('crPhone').value.trim();
    return !!($('agree').checked && nm && phOk(ph) && $('crA1').checked && $('crA2').checked); }
  // 2026.10.26 태형 '조금은 여유있게': 전화는 숫자 8자리 이상이면 띄어쓰기·하이픈·메모가 섞여도 통과, 이메일은 @ 앞뒤에 글자만 있으면 통과
  function phOk(ph){ return ph.replace(/\D/g,'').length>=8 || /\S@\S/.test(ph); }
  function info(){ var ok=infoOk(); $('crType').disabled=!ok; $('crType').style.opacity=ok?'':'.45'; $('crInfoMsg').hidden=ok || !$('agree').checked;
    var ph=$('crPhone').value.trim(); $('crInfoMsg').textContent=(ph && !phOk(ph))? '연락처는 전화번호나 이메일로 적어 주시면 다음으로 넘어갑니다.' : '성함·연락처를 넣고 동의해 주시면 다음으로 넘어갑니다.'; types(); }
  ['crName','crPhone'].forEach(function(id){ $(id).addEventListener('input',info); }); ['crA1','crA2'].forEach(function(id){ $(id).addEventListener('change',function(){ $('crAll').checked=$('crA1').checked&&$('crA2').checked; info(); }); });
  $('crAll').addEventListener('change',function(){ $('crA1').checked=$('crA2').checked=$('crAll').checked; info(); });   // 2026.10.23 전체 동의 하나로(다른 신청서와 같은 틀)
  // 3) 유형 + 확인할 항목(2026.10.23 항목 선택형: 안 받음·받음·모름)
  var ITEMS=[{k:'st',g:'b',nm:'창업중소기업 세액감면',sub:'창업 후 5년간 소득세·법인세 50~100% 세액감면'},{k:'sp',g:'b',nm:'중소기업 특별세액감면',sub:'업종·지역별 소득세·법인세 5~30% 세액감면'},{k:'jb',g:'b',nm:'고용증대·통합고용세액공제',sub:'2021~2025년 상시근로자 증가 시 세액공제'},
             {k:'dep',g:'w',nm:'부양가족 공제',sub:'연말정산 시 누락한 부모님 기본공제'},{k:'rent',g:'w',nm:'월세 세액공제',sub:'연말정산 시 누락한 월세 세액공제'},{k:'sme',g:'w',nm:'중소기업 취업자 소득세 감면',sub:'중소기업에 취업한 청년 등 5년(3년)간 소득세 70~90% 감면'}];
  (function(){ var h='<div class="cr-irow hd"><div>항목</div><div>안 받음</div><div>받음</div><div>모름</div></div>';
    ITEMS.forEach(function(it){ h+='<div class="cr-irow" data-g="'+it.g+'" data-k="'+it.k+'"><div><b>'+it.nm+'</b><small>'+it.sub+'</small><small class="cr-na" hidden></small></div>'+
      [['none','안 받음'],['got','받음'],['unk','모름']].map(function(x){ return '<label><input type="radio" name="crm_'+it.k+'" value="'+x[0]+'">'+x[1]+'</label>'; }).join('')+'</div>'; });
    $('crItemRows').innerHTML=h; })();
  // 2026.10.26 태형: 창업감면·중소기업 특별세액감면은 같은 해에 하나만(조세특례제한법 제127조제5항)
  $('crItemRows').insertAdjacentHTML('afterend','<div class="cr-warn" id="crBothGot" hidden>창업감면과 중소기업 특별세액감면은 <b>같은 해에 하나만</b> 받을 수 있습니다. 창업감면 기간(5년)이 끝난 뒤 특별세액감면을 받으셨다면 그대로 두시면 됩니다.</div>');
  function bothGot(){ $('crBothGot').hidden=!(mode('st')==='got' && mode('sp')==='got'); }
  [].forEach.call(document.querySelectorAll('input[name=crm_st],input[name=crm_sp]'),function(e){ e.addEventListener('change',bothGot); });
  // 2026.10.26 태형: 12월 말 인원 선택지는 헷갈려서 없앰 — 연평균으로만 입력·계산하고 안내만 표시
  $('crBizTbl').parentNode.insertAdjacentHTML('afterend','<p class="cr-note cr-avg" id="crCntWrap" hidden>⚠ 직원 수는 그해 <b>12월 말 인원</b>을 입력해 주세요. 공제액은 채용한 달에 따라 달라지므로, 연초(1월) 채용과 연중(7월) 채용 기준으로 범위를 보여 드립니다.</p>');
  var BOTH='<p class="cr-note">창업감면과 중소기업 특별세액감면을 둘 다 받으셨다고 고르셨습니다. 같은 해에는 둘 중 하나만 받을 수 있어(조세특례제한법 제127조제5항), 같은 해에 둘 다 받으셨다면 나중에 다시 내야 할 수도 있습니다. 세무사 검토가 필요합니다.</p>';
  function mode(k){ var e=document.querySelector('input[name=crm_'+k+']:checked'); var row=e&&e.closest('.cr-irow'); return (e && row && !row.hidden && !row.classList.contains('na'))? e.value : ''; }
  function comp(k){ var m=mode(k); return m==='none'||m==='unk'; }
  function got(k){ return mode(k)==='got'; }
  document.querySelectorAll('#crItemRows input').forEach(function(i){ i.addEventListener('change',types);
    // 이미 고른 칸을 다시 누르면 선택 해제(그 항목은 확인 안 함)
    i.addEventListener('mousedown',function(){ i._was=i.checked; }); i.addEventListener('keydown',function(){ i._was=false; });
    i.addEventListener('click',function(){ if(i._was){ i.checked=false; i._was=false; types(); } }); });
  $('crAllUnk').addEventListener('click',function(){ document.querySelectorAll('#crItemRows .cr-irow:not([hidden]):not(.na) input[value=unk]').forEach(function(i){ i.checked=true; }); types(); });
  function needVis(){
    var any=comp('st')||comp('sp')||comp('jb');
    document.querySelectorAll('#crBiz [data-need]').forEach(function(el){ var ks=el.getAttribute('data-need').split(' '); el.hidden = ks[0]==='any' ? !any : !ks.some(comp); });
    $('crBizNone').hidden = any; var wany=comp('dep')||comp('rent')||comp('sme'); $('crWorkNone').hidden=wany; $('crWorkTbl').parentNode.hidden=!wany; if($('crSme')) $('crSme').hidden=!comp('sme');
  }
  function types(){ var on=!$('crType').disabled, t=on?checked('crt'):[];
    var hb=t.indexOf('p')>=0||t.indexOf('c')>=0, hw=t.indexOf('w')>=0;
    // 2026.10.27 태형 '사업자 기본정보를 먼저': 개업 연월·업종·소재지를 고른 뒤에 항목 표를 보여 주고, 해당 없는 항목은 회색으로 이유 표시
    var baseOk = hb && !!($('crOpenY').value && $('crOpenM').value && $('crInd').value && $('crReg').value);
    $('crBase').hidden=!hb; $('crBaseMsg').hidden=baseOk; gate();
    document.querySelectorAll('#crItemRows .cr-irow[data-g]').forEach(function(r){ r.hidden = r.getAttribute('data-g')==='b' ? !baseOk : !hw; });
    $('crItems').hidden=!(baseOk||hw);
    var b=hb && ['st','sp','jb'].some(function(k){return mode(k)}), w=hw && ['dep','rent','sme'].some(function(k){return mode(k)});
    needVis(); workCols();
    $('crBiz').hidden=!b; $('crWork').hidden=!w; $('crGoBox').hidden=!(b||w); $('crTypeMsg').hidden=!on||t.length>0;
    $('crBizKind').textContent = (t.indexOf('p')>=0&&t.indexOf('c')>=0)?'(둘 다라면 주된 사업 하나만 넣어 주세요. 나머지는 상담에서 같이 봅니다)':(t.indexOf('c')>=0?'(법인사업자)':'(개인사업자)');
    if(b) bizTable(true); check(); renum(); }
  function renum(){ var i=1; ['crInfo','crType','crBase','crItems','crBiz','crWork'].forEach(function(id){ var f=$(id); if(f && !f.hidden){ var s=f.querySelector('.c-q > span'); if(s) s.textContent=i; i++; } }); }
  // 창업감면·중소기업 특별세액감면이 해당 없는 경우(업종·감면 기간) — 항목 표에서 회색으로 막고 이유를 보여 줌
  function gate(){ var y=n($('crOpenY').value), m=n($('crOpenM').value)||1, ind=$('crInd').value, fi=n($('crFirstInc').value), R={st:'',sp:''};
    if(y){ var old = y<2018 || (y===2018 && m<=5);
      if(ind==='retail') R.st='일반 소매업은 창업감면 대상 업종이 아닙니다.';
      else if(old && (ind==='online'||ind==='beauty')) R.st='2018년 5월 29일 전에 창업한 경우 통신판매업·미용업은 창업감면 대상 업종이 아닙니다.';
      else { var FI=Math.min(fi||y, y+(m>1?5:4)); if(FI+4<2021) R.st='감면 기간(처음 소득이 난 해부터 5년)이 2021년 전에 끝났습니다.'+(fi?'':' 개업 초기에 적자였다면 위에서 최초 소득 발생 연도를 바꿔 주세요.'); }
      if(ind==='food'||ind==='beauty') R.sp='음식점·미용실 등은 중소기업 특별세액감면 대상 업종이 아닙니다.'; }
    ['st','sp'].forEach(function(k){ var row=document.querySelector('#crItemRows .cr-irow[data-k='+k+']'); if(!row) return; var na=!!R[k], el=row.querySelector('.cr-na');
      row.classList.toggle('na',na); el.hidden=!na; el.textContent=R[k]; row.querySelectorAll('input').forEach(function(i){ i.disabled=na; if(na) i.checked=false; }); }); }
  document.head.insertAdjacentHTML('beforeend','<style>.cr-irow.na>label{opacity:.35}.cr-irow.na b{color:#888}.cr-irow small.cr-na{display:block;color:#666;font-weight:700;margin-top:3px}.cr-yt td,.cr-yt th{white-space:nowrap}.cr-det .cr-yt td:first-child,.cr-det .cr-yt th:first-child{position:sticky;left:-14px;background:var(--bg,#fff);z-index:1}</style>');
  document.querySelectorAll('input[name=crt]').forEach(function(i){ i.addEventListener('change',types); });
  // 개업 연월
  var oy=$('crOpenY'); oy.innerHTML='<option value="">연도</option>'+(function(){var s='';for(var y=2025;y>=1990;y--) s+='<option value="'+y+'">'+y+'년</option>';return s})();
  $('crOpenM').innerHTML='<option value="">월</option>'+[1,2,3,4,5,6,7,8,9,10,11,12].map(function(m){return '<option value="'+m+'">'+m+'월</option>'}).join('');
  function bizYears(){ var y=n(oy.value); if(!y) return []; return YEARS.filter(function(t){return t>=y}); }
  function taxLabel(){ var c=checked('crt'); return (c.indexOf('c')>=0&&c.indexOf('p')<0)?'납부한 법인세':'납부한 종합소득세'; }
  var lastKey='', store={};
  function bizTable(keep){
    var ys=bizYears(), y0=n(oy.value), tb=$('crBizTbl'), cR=comp('st')||comp('sp'), cS=comp('jb'), key=(y0||'')+'|'+taxLabel()+'|'+cR+'|'+cS;
    if(keep && key===lastKey) return;
    tb.querySelectorAll('input').forEach(function(i){ store[i.getAttribute('data-k')+i.getAttribute('data-t')]=i.value; }); var old=store;   // 2026.10.23 개업 연도를 바꿨다 되돌려도 값 유지
    lastKey=key;
    if(!ys.length){ tb.innerHTML=''; $('crBizHint').textContent='개업 연도를 선택하시면 입력할 연도가 표시됩니다.'; check(); return; }
    function inp(k,t,ph){ var v=old[k+t]||''; var L={rev:'매출(원)',tax:taxLabel()+'(원)',y:'청년 등 직원 수',o:'그 외 직원 수'}[k]; return '<input data-k="'+k+'" data-t="'+t+'" inputmode="'+((k==='y'||k==='o')?'decimal':'numeric')+'" placeholder="'+ph+'" aria-label="'+t+'년 '+L+'" value="'+v+'">'; }
    var h='<tr><th>연도</th>'+(cR?'<th>매출 (원)</th>':'')+'<th>'+taxLabel()+' (원)</th>'+(cS?'<th>청년 등 직원 (명)<br><small>34세 이하 정규직 직원 등<br>(2022년까지는 29세 이하)</small></th><th>그 외 직원 (명)</th>':'')+'</tr>';
    ys.forEach(function(t){ h+='<tr><td>'+t+'</td>'+(cR?'<td>'+inp('rev',t,'예: 70,000,000')+'</td>':'')+'<td>'+inp('tax',t,'예: 1,740,000')+'</td>'+(cS?'<td>'+inp('y',t,'0')+'</td><td>'+inp('o',t,'0')+'</td>':'')+'</tr>'; });
    if(cS && y0 && y0<=2020){ var cmp=function(t){ return '<tr><td>'+t+'<br><small>비교용</small></td>'+(cR?'<td>-</td>':'')+'<td>-</td><td>'+inp('y',t,'모르면 비움')+'</td><td>'+inp('o',t,'모르면 비움')+'</td></tr>'; }; h=h.replace('</tr>','</tr>'+(y0<=2019?cmp(2019):'')+cmp(2020)); }   // 2026.10.27 2019·2020년 말 인원(비교용)   // 2026.10.26 2021년 증가분 비교용 2020년 말 인원
    tb.innerHTML=h; if($('crCntWrap')) $('crCntWrap').hidden=!cS;
    $('crBizHint').textContent = !cS ? '개업한 해부터 2025년까지(2021년 전 개업이면 2021~2025년)만 입력합니다.' : y0<=2020 ? (y0<=2019 ? '2021년 전에 개업하셨으면 경정청구가 가능한 2021~2025년만 입력하고, 비교용으로 2019·2020년 말 직원 수도 입력해 주세요. 2020년에 늘어난 직원은 2021~2022년에도 공제됩니다(모르면 비워 두시면 그 몫은 계산하지 않습니다). 직원 수는 사업주 본인을 빼고 그해 12월 말 인원입니다.' : '2020년에 개업하셨으면 경정청구가 가능한 2021~2025년만 입력하고, 비교용으로 2020년 말 직원 수도 입력해 주세요. 2020년에 늘어난 직원은 2021~2022년에도 공제됩니다(모르면 비워 두시면 그 몫은 계산하지 않습니다). 직원 수는 사업주 본인을 빼고 그해 12월 말 인원입니다.') : '개업한 해부터 2025년까지만 입력합니다. 직원 수는 사업주 본인을 빼고 그해 12월 말 인원입니다.';
    tb.querySelectorAll('input').forEach(function(i){ i.addEventListener('input',check); }); if($('crCntEnd')&&!$('crCntEnd').__on){ $('crCntEnd').__on=1; $('crCntEnd').addEventListener('change',check); }
    check();
  }
  function fiOpts(){ var y=n(oy.value), el=$('crFirstInc'), cur=el.value, h='<option value="">개업한 해와 같음</option>'; if(y){ for(var k=y+1;k<=Math.min(2025,y+((n($('crOpenM').value)||1)>1?5:4));k++) h+='<option value="'+k+'">'+k+'년</option>'; } el.innerHTML=h; if([].some.call(el.options,function(op){return op.value===cur})) el.value=cur; }
  oy.addEventListener('change',function(){ fiOpts(); bizTable(false); types(); }); fiOpts();
  ['crOpenM','crInd','crReg','crFirstInc'].forEach(function(id){ $(id).addEventListener('change',function(){ if(id==='crOpenM') fiOpts(); types(); }); });   // 2026.10.27 기본정보가 바뀌면 항목 표 다시 판단(1월 아닌 달 개업이면 최초 소득 연도는 개업 연도+5년까지)
  ['crOpenM','crFirstInc','crInd','crReg','crFirst','crBook','crLate','crGot'].forEach(function(id){ $(id).addEventListener('change',check); });
  ['crAge','crMil'].forEach(function(id){ $(id).addEventListener('input',check); });
  // 근로자 표
  (function(){ var h='<tr><th>연도</th><th>총급여(연봉)</th><th>납부세액<br><small>결정세액 (원)</small></th><th>누락한<br>부모님 수</th><th>그중<br>70세 이상</th><th>월세<br><small>월 (원)</small></th></tr>';
    var cnt='<option value="0">0명</option><option value="1">1명</option><option value="2">2명</option><option value="3">3명</option><option value="4">4명</option>';
    YEARS.forEach(function(t){ h+='<tr><td>'+t+'</td><td><select data-k="g" data-t="'+t+'"><option value="">연말정산 안 함</option><option value="a">5,500만 원 이하</option><option value="b">5,500만 원 초과~7천만 원 이하</option><option value="c">7천만 원 초과~8천만 원 이하</option><option value="d">8천만 원 초과</option></select></td><td><input data-k="paid" data-t="'+t+'" inputmode="numeric" placeholder="모름"></td><td><select data-k="par" data-t="'+t+'">'+cnt+'</select></td><td><select data-k="old" data-t="'+t+'">'+cnt+'</select></td><td><input data-k="rent" data-t="'+t+'" inputmode="numeric" placeholder="0"></td></tr>'; });
    $('crWorkTbl').innerHTML=h; $('crWorkTbl').querySelectorAll('input,select').forEach(function(i){ i.addEventListener(i.tagName==='SELECT'?'change':'input',check); });
  })();
  // 2026.11.02 중소기업 취업자 감면 입력(근로자 표 아래)
  (function(){ var yo=function(a,b,first){ var h='<option value="">연도</option>'+(first||''); for(var y=b;y>=a;y--) h+='<option value="'+y+'">'+y+'년</option>'; return h; }, mo='<option value="">월</option>'+[1,2,3,4,5,6,7,8,9,10,11,12].map(function(m){return '<option value="'+m+'">'+m+'월</option>'}).join('');
    $('crWorkTbl').parentNode.insertAdjacentHTML('afterend','<div id="crSme" hidden style="margin:14px 0 4px;padding:12px 14px;border:1.5px solid var(--line,#ddd);border-radius:10px"><p style="margin:0 0 10px;font-weight:800">중소기업 취업자 소득세 감면 정보</p><div class="cr-grid2">'+
      '<label>대상<select id="crSmeK"><option value="">눌러서 선택</option><option value="y">청년 (취업 당시 만 34세 이하)</option><option value="o">60세 이상·장애인·경력단절 여성</option><option value="u">잘 모르겠음</option></select></label>'+
      '<label>그 회사에 처음 취업한 연월<span class="cr-ym"><select id="crSmeY">'+yo(2016,2025,'<option value="2015">2015년 이전</option>')+'</select><select id="crSmeM">'+mo+'</select></span></label>'+
      '<label>회사 업종<select id="crSmeI"><option value="">눌러서 선택</option><option value="ok">제조·건설·도소매·운수·숙박·음식·IT·광고 등</option><option value="no">병원·의원, 법무·회계·세무, 금융·보험, 일반 학원, 공공기관</option><option value="u">잘 모르겠음</option></select></label>'+
      '<label>회사에 감면 신청을 했나요?<select id="crSmeR"><option value="">눌러서 선택</option><option value="never">한 번도 안 함</option><option value="mid">다니던 중간부터 함</option><option value="unk">잘 모르겠음</option></select></label>'+
      '<label hidden id="crSmeRW">감면 신청을 시작한 연도<select id="crSmeRY">'+yo(2016,2026)+'</select></label>'+
      '<label>지금은<select id="crSmeQ"><option value="">눌러서 선택</option><option value="in">그 회사에 다니는 중</option><option value="out">퇴사함</option></select></label>'+
      '</div><p class="hint" style="margin:10px 0 0">청년 나이는 군 복무 기간(최대 6년)을 빼고 셉니다. 위 표에는 그 회사에서 받은 해의 총급여 구간과 결정세액을 넣어 주세요. 회사 업종이 정해져 있고, 대표의 가족이나 임원은 빠집니다.</p></div>');
    ['crSmeK','crSmeI','crSmeY','crSmeM','crSmeR','crSmeRY','crSmeQ'].forEach(function(id){ $(id).addEventListener('change',function(){ $('crSmeRW').hidden=$('crSmeR').value!=='mid'; check(); }); });
  })();
  function workCols(){ var d=comp('dep'), r=comp('rent'), tb=$('crWorkTbl'); if(!tb.rows.length) return;
    [].forEach.call(tb.rows,function(tr){ [3,4].forEach(function(c){ if(tr.cells[c]) tr.cells[c].hidden=!d; }); if(tr.cells[5]) tr.cells[5].hidden=!r; }); }
  function cell(tb,k,t){ return tb.querySelector('[data-k="'+k+'"][data-t="'+t+'"]'); }
  // 입력 확인 → 비어 있으면 결과 버튼 잠금 + 빨간 표시
  function collect(){
    var miss=[], bad=[], t=checked('crt'), o={};
    function need(id,label){ var e=$(id); var lb=e.closest('label'); if(lb&&lb.hidden) return ''; if(!e.value.trim()){ miss.push(label); bad.push(e); } return e.value.trim(); }
    var bSel={st:comp('st'),sp:comp('sp'),jb:comp('jb')}, bGot={st:got('st'),sp:got('sp'),jb:got('jb')}, wSel={dep:comp('dep'),rent:comp('rent'),sme:comp('sme')}, wGot={dep:got('dep'),rent:got('rent'),sme:got('sme')};
    var hb=t.indexOf('p')>=0||t.indexOf('c')>=0, hw=t.indexOf('w')>=0;
    if((hb||hw) && !['st','sp','jb','dep','rent','sme'].some(function(k){return mode(k)})) miss.push('확인할 항목(안 받음·받음·모름 중 하나라도)');
    if(hb && !(bSel.st||bSel.sp||bSel.jb) && (bGot.st||bGot.sp||bGot.jb)) o.bizGot={kind:(t.indexOf('c')>=0&&t.indexOf('p')<0)?'c':'p', got:bGot};
    if(hb && (bSel.st||bSel.sp||bSel.jb)){
      var b={kind:(t.indexOf('c')>=0&&t.indexOf('p')<0)?'c':'p', sel:bSel, gotI:bGot};
      var y=need('crOpenY','개업 연도'), m=bSel.st?need('crOpenM','개업 월'):($('crOpenM').value||'1'); b.open={y:n(y),m:n(m)};   // 개업 월은 창업감면(첫해 환산·감면기간)에만 필요
      b.firstInc=n($('crFirstInc').value)||0; b.ind=need('crInd','업종'); b.reg=need('crReg','사업장 소재지'); b.first=need('crFirst','최초 창업 여부');
      b.age=n(need('crAge','창업 당시 만 나이')); var mil=$('crMil').value.trim(); if(mil==='' && !$('crMil').closest('label').hidden){ miss.push('병역 이행 기간(없으면 0)'); bad.push($('crMil')); } b.mil=n(mil)||0;
      b.book=need('crBook','신고 방식')||'book'; b.late=need('crLate','신고기한 준수 여부')||'ok'; b.got=(bGot.st||bGot.sp||bGot.jb)?'y':'n'; b.first=b.first||'y'; b.ind=b.ind||'etc'; b.reg=b.reg||'unk'; b.age=b.age||99;
      var tb=$('crBizTbl'); bizTable(true); b.rows={}; b.base={y:0,o:0}; b.cntEnd=true; /* 2026.10.26 입력은 12월 말 인원 한 가지, 결과는 항상 범위 */ var rowMiss=false;
      if(b.open.y&&b.open.y<=2020){ var c20y=cell(tb,'y',2020), c20o=cell(tb,'o',2020); b.base = (c20y&&(c20y.value.trim()!==''||c20o.value.trim()!==''))? {y:n(c20y.value)||0, o:n(c20o.value)||0} : null;
        var c19y=cell(tb,'y',2019), c19o=cell(tb,'o',2019); b.base0 = b.open.y===2020 ? {y:0,o:0} : (c19y&&(c19y.value.trim()!==''||c19o.value.trim()!==''))? {y:n(c19y.value)||0, o:n(c19o.value)||0} : null; }   // 2020년 개업이면 2019년 말은 0명   // 비우면 2021년 증가분은 계산 안 함
      bizYears().forEach(function(yr){ var r={}; if(!cell(tb,'tax',yr)) return;
        ['rev','tax'].forEach(function(k){ var e=cell(tb,k,yr); if(!e){ r[k]=null; return; } if(e.value.trim()===''){ rowMiss=true; bad.push(e); } var v=n(e.value); r[k]=v==null?null:v/10000; });   // 입력은 원, 계산은 만원
        r.y=cell(tb,'y',yr)?(n(cell(tb,'y',yr).value)||0):0; r.o=cell(tb,'o',yr)?(n(cell(tb,'o',yr).value)||0):0; b.rows[yr]=r; });
      if(rowMiss) miss.push((bSel.st||bSel.sp)?'연도별 매출·납부세액(대략, 없으면 0)':'연도별 납부세액(대략, 없으면 0)');
      // 2023년에 직원이 늘었는지 비교하려면 2022년 말 직원 수가 필요(비우면 0명으로 보여 크게 잡힘)
      if(bSel.jb&&b.open.y&&b.open.y<=2022&&cell(tb,'y',2022)){ var later=[2023,2024,2025].some(function(k){return b.rows[k]&&(b.rows[k].y||b.rows[k].o);});
        if(later && (cell(tb,'y',2022).value.trim()===''||cell(tb,'o',2022).value.trim()==='')){ miss.push('2022년 말 직원 수(2023년과 비교용, 없으면 0)'); bad.push(cell(tb,'y',2022)); bad.push(cell(tb,'o',2022)); } }
      o.biz=b;
    }
    if(hw && !(wSel.dep||wSel.rent||wSel.sme) && (wGot.dep||wGot.rent||wGot.sme)) o.workGot=wGot;
    if(hw && (wSel.dep||wSel.rent||wSel.sme)){
      var w={rows:{}, sel:wSel, gotI:wGot}, tw=$('crWorkTbl'), any=false;
      YEARS.forEach(function(yr){ var g=cell(tw,'g',yr).value; if(!g) return; any=true;
        w.rows[yr]={g:g, paid:(cell(tw,'paid',yr).value.trim()===''? -1 : (n(cell(tw,'paid',yr).value)||0)/10000), par:n(cell(tw,'par',yr).value)||0, old:n(cell(tw,'old',yr).value)||0, rent:(n(cell(tw,'rent',yr).value)||0)/10000}; });   // 원 → 만원
      YEARS.forEach(function(yr){ var x=w.rows[yr]; if(x && x.old>x.par){ miss.push('근로자 '+yr+'년: 70세 이상 인원이 누락한 부모님 수보다 많습니다'); bad.push(cell(tw,'old',yr)); } });   /* 2026.10.27 재검토(2차) */
      if(wSel.sme){ var sk=need('crSmeK','중소기업 취업자: 대상'), si=need('crSmeI','중소기업 취업자: 회사 업종'), sy=need('crSmeY','중소기업 취업자: 취업 연도'), smm=need('crSmeM','중소기업 취업자: 취업 월'), sr=need('crSmeR','중소기업 취업자: 감면 신청 여부'), sq=need('crSmeQ','중소기업 취업자: 지금 재직 여부');
        var sry=sr==='mid'?need('crSmeRY','중소기업 취업자: 신청 시작 연도'):'';
        w.sme={kind:sk, ind:si, y:n(sy), m:n(smm)||1, req:sr, ry:n(sry), quit:sq==='out'};
        if(sr==='mid' && sry && sy && n(sry) < n(sy)){ miss.push('중소기업 취업자: 신청 시작 연도가 취업 연도보다 빠릅니다'); bad.push($('crSmeRY')); } }
      if(!any){ miss.push('근로자: 연말정산한 해의 총급여 구간'); YEARS.forEach(function(yr){ bad.push(cell(tw,'g',yr)); }); }
      o.work=w;
    }
    if(!t.length) miss.push('해당하는 것(개인사업자·법인사업자·근로자)');
    return {o:o, miss:miss, bad:bad};
  }
  var tried=false;
  function check(){
    document.querySelectorAll('#cr .bad').forEach(function(e){e.classList.remove('bad')});
    if(!infoOk()){ $('crGo').classList.add('off'); if($('crGo2')) $('crGo2').classList.add('off'); return null; }
    var c=collect(); $('crGo').classList.toggle('off',c.miss.length>0); if($('crGo2')) $('crGo2').classList.toggle('off',c.miss.length>0); $('crGo').setAttribute('aria-disabled',c.miss.length>0?'true':'false');
    $('crGoMsg').textContent = c.miss.length? '다음 항목을 입력해 주세요: '+c.miss.join(', ') : '';
    if(tried) c.bad.forEach(function(e){ if(e) e.classList.add('bad'); });
    return c;
  }
  // 기한(2026년 기준): 개인사업자 다음 해 5월 31일 + 5년, 법인(12월 결산) 3월 31일 + 5년, 근로자 연말정산 납부기한(다음 해 3월 10일) + 5년
  function dl(kind,t){ return kind==='c'? (t+6)+'년 3월 31일' : kind==='w'? (t+6)+'년 3월 10일 무렵' : (t+6)+'년 5월 31일'; }
  var LV={hi:['가능성 있음','hi'],chk:['확인 필요','chk'],no:['해당 없음','no']};
  function amt(a,b){ a=Math.round(a); b=Math.round(b); return (a<=0&&b>0)? '최대 약 '+man(b)+' <small style="font-size:13px;font-weight:600">(0원일 수도 있습니다)</small>' : rng(a,b); }
  var GOT={st:['청년 나이를 병역 이행 기간(최대 6년)을 빼고 계산했는지 확인합니다. 빼면 청년이 되어 감면율이 올라갈 수도 있습니다.','매출이 기준 이하인 해에 생계형(수도권 밖 100%)으로 받았는지 확인합니다.','감면 기간 5년(최초 소득 발생 연도부터)을 다 받았는지 확인합니다.','같은 해 고용증대·통합고용세액공제도 함께 받을 수 있었는지 확인합니다(2024년까지 창업한 경우).'],
    sp:['업종과 지역에 맞는 감면율(예: 수도권 밖 제조업 30%)로 받았는지 확인합니다.','창업감면 기간과 겹치는 해에 더 큰 쪽을 골랐는지 확인합니다.','고용증대·통합고용세액공제를 함께 받았는지 확인합니다(함께 받을 수 있습니다).'],
    jb:['한 달 60시간 이상 일하는 단시간 근로자를 0.5명(요건을 갖추면 0.75명)으로 반영했는지 확인합니다.','60세 이상·장애인·경력단절 여성을 청년 등(높은 단가)으로 반영했는지 확인합니다.','청년 나이를 병역 이행 기간(최대 6년)을 빼고 계산했는지 확인합니다.','늘어난 해 다음 2년(2·3년 차) 공제를 누락하지 않았는지 확인합니다.','기간제의 정규직 전환·육아휴직 복귀자 공제를 따로 받을 수 있었는지 확인합니다.','납부세액이 적어 받지 못한 공제가 다음 해로 이월되어 공제됐는지 확인합니다.'],
    dep:['70세 이상 부모님의 경로우대 추가공제(1명당 100만 원)가 누락됐는지 확인합니다.','장애인 추가공제(1명당 200만 원)가 누락됐는지 확인합니다.','형제와 중복되지 않았는지 확인합니다(중복이면 한 사람만 받을 수 있습니다).'],
    sme:['감면 기간(청년 5년, 그 외 3년)을 끝까지 받았는지 확인합니다.','다니던 중간에 신청해 그 앞 기간이 빠지지 않았는지 확인합니다.','연 한도(2022년분까지 150만 원, 2023년분부터 200만 원)까지 반영됐는지 확인합니다.','퇴사하셨어도 회사 협조 없이 직접 신청할 수 있습니다.'],
    rent:['그 해 총급여에 맞는 공제율로 받았는지 확인합니다(5,500만 원 이하 17%, 2021년분은 12%).','공제 한도까지 반영했는지 확인합니다(2024년분부터 연 1,000만 원).','월세 세액공제를 받으면 표준세액공제 13만 원은 적용되지 않아 비교가 필요합니다.']};
  var GOTNM={st:'창업중소기업 세액감면',sp:'중소기업 특별세액감면',jb:'고용증대·통합고용세액공제',dep:'부양가족 공제',rent:'월세 세액공제',sme:'중소기업 취업자 소득세 감면'};
  function gotCard(k){ return '<div class="cr-card cr-got chk"><p class="cr-h"><b>'+GOTNM[k]+'</b><em>이미 받음 · 검토</em></p><p class="cr-why">이미 받으셨어도 아래가 빠졌다면 더 돌려받을 수도 있습니다. 세무사 검토가 필요한 부분이라 금액은 계산하지 않았습니다.</p><ul>'+GOT[k].map(function(x){return '<li>'+x+'</li>';}).join('')+'</ul></div>'; }
  function card(title,it,extra,pre){ if(!it||it.lv==='off') return ''; var lv=LV[it.lv]; return '<div class="cr-card '+lv[1]+'"><p class="cr-h"><b>'+title+'</b><em>'+lv[0]+'</em></p>'+
      (it.lv==='no'? '<p class="cr-why">'+it.why+'</p>' : (pre&&it.max>0?'<p class="cr-why" style="margin:0">감면·공제 금액 (납부세액·최저한세 한도 적용 전)</p>':'')+'<p class="cr-amt">'+(it.max>0?amt(it.min,it.max):'금액은 상담에서 확인')+'</p>'+(it.why?'<p class="cr-why">'+it.why+'</p>':'')+(it.why2?'<p class="cr-why">'+it.why2+'</p>':'')+(it.why3?'<p class="cr-why">'+it.why3+'</p>':'')+(extra||''))+'</div>'; }
  function run(){
    tried=true; lastMemo=''; var c=check(); if(!c||c.miss.length){ if(c&&c.bad[0]&&c.bad[0].focus) c.bad[0].focus(); return; }
    var o=c.o, html='', memo=[], tot=[0,0];
    if(o.biz){ var b=o.biz, r=C.biz(b), kindNm=b.kind==='c'?'법인사업자':'개인사업자';
      tot[0]+=r.total[0]; tot[1]+=r.total[1];
      if(r.items.st.lv!=='no') r.items.st.why = r.oldReg?'2018년 5월 이전 창업은 그때 법(종전 규정)이 적용돼 과밀억제권역 밖에서만 50%로 계산했습니다. 정확한 창업일(5월 29일 전후)은 상담에서 확인합니다.':(r.youthMaybe?'병역 이행 기간을 빼면 만 34세 경계라 생일에 따라 청년 여부가 갈려, 청년인 경우와 아닌 경우를 함께 범위로 보여 드립니다.':r.youth?'청년 창업으로 계산했습니다(병역 이행 기간을 빼고 만 34세 이하).':'청년이 아니어서 생계형(매출이 기준 이하인 해, 첫해는 1년으로 환산) 또는 일반 창업감면으로 계산했습니다.');
      if(((r.oldReg && b.open.y===2018 && b.open.m===5) || r.youthMaybe) && r.items.st.lv==='hi') r.items.st.lv='chk';
      var chkNotes=[];
      if(b.gotI&&b.gotI.st&&b.sel.sp&&r.items.sp.lv!=='no'){ r.items.sp.lv='chk'; r.items.sp.why=(r.items.sp.why||'')+'창업감면을 이미 받으셨다고 고르셔서, 창업감면 기간(5년) 안의 해는 중소기업 특별세액감면을 빼고 계산했습니다(같은 해에는 하나만 받을 수 있습니다). 세무사 검토가 필요합니다.'; }
      if(b.gotI&&b.gotI.sp&&b.sel.st&&r.items.st.lv!=='no'){ r.items.st.lv='chk'; chkNotes.push('이미 중소기업 특별세액감면을 받은 해는 창업감면이 더 클 때 그 차액만 돌려받을 수 있습니다. 세무사 검토가 필요합니다.'); }
      if(b.gotI&&b.gotI.st&&b.sel.jb&&b.open.y>=2025&&r.items.jb.lv!=='no'){ r.items.jb.lv='chk'; r.items.jb.why3=(r.items.jb.why3||'')+' 2025년 이후 창업으로 창업감면을 받으셨다면 고용 공제는 함께 받을 수 없어 0원으로 계산했습니다.'; }
      if(r.oldReg) chkNotes.push('2018년 5월 29일 전 창업은 그때 법이 적용됩니다. 그때 기준으로 청년창업기업이었다면 처음 3년은 75%일 수도 있어, 감면율은 세무사 검토가 필요합니다.');
      if(r.annAmb) chkNotes.push('개업한 첫해 매출을 1년으로 환산해 생계형 기준과 비교할지는 판단이 갈리는 부분이라, 두 경우를 범위로 보여 드립니다. 세무사 검토가 필요합니다.');
      if(r.corpYouth) chkNotes.push('법인은 대표자가 청년이면서 최대주주(지배주주)여야 청년창업으로 인정됩니다. 주주 구성은 세무사 검토가 필요합니다.');
      if(chkNotes.length && r.items.st.lv!=='no') r.items.st.why=(r.items.st.why||'')+' '+chkNotes.join(' ');
      if(r.jbTDrop && r.items.jb.lv!=='no') r.items.jb.why3='공제받은 뒤 2년 안에 전체 직원 수가 줄어든 해가 있어, 줄어든 해부터는 공제를 빼고, 이미 받은 공제 중 다시 내야 하는 금액(추징)도 그 해 환급 예상액에서 뺐습니다. 추징액은 시행령 계산식으로 대략 계산했으므로 세무사 검토가 필요합니다.';   // 2026.10.26 전체 감소와 청년 등만 감소를 나눠 안내
      if(r.jbYDrop && r.items.jb.lv!=='no') r.items.jb.why3=(r.items.jb.why3||'')+' 청년 등 직원 수가 줄어든 해부터는 그 외 직원 단가로 낮춰 계산했습니다. 나이(34세 초과) 때문에 줄어든 경우에는 추징이 없고, 퇴사 등 다른 이유로 줄어든 경우에는 이미 받은 공제 중 차액을 다시 내야 해서, 두 경우를 범위로 보여 드립니다. 심판례에 따라 더 유리하게 계산될 수도 있어 세무사 검토가 필요합니다.';   // 2026.10.26 시행령 제26조의8⑤는 추징 계산에만 청년으로 봄 — 공제 계속 여부는 판단이 갈림(조심-2023-광-8267 등)
      if(b.ind==='it' && !r.youth && b.reg!=='over' && b.open.y<=2024 && r.items.st.lv!=='no') r.items.st.why2='소프트웨어 개발 등 신성장 서비스업이면 처음 3년은 75%까지 감면될 수도 있어 상담에서 확인합니다.';
      // 2026.10.26 태형 '설명이 장황 → 중요한 것 위로': 핵심만 짧은 목록, 계산 기준은 접어 둠
      if(r.items.jb.lv!=='no'){ var J=r.items.jb, K=[], jover=Object.keys(r.years).some(function(t){return r.years[t].over});
        K.push('<b>실제로 돌려받는 금액은 이보다 줄어듭니다.</b> 고용 공제액의 20%는 농어촌특별세로 내야 해서 맨 위 합계와 연도별 환급 예상액에서는 뺐습니다(항목별 금액은 빼기 전 금액입니다).'+(jover?' 납부세액·최저한세 한도를 넘는 부분은 맨 위 합계에서 뺐습니다.':''));
        if(J.est) K.push('장부 없이(추계) 신고하신 해는 고용 공제를 받을 수 없어 최소 금액을 0원으로 잡았습니다. 장부로 다시 맞출 수 있는지는 상담에서 확인합니다.');
        else if(b.cntEnd) K.push('직원을 연초(1월)에 채용·퇴사한 경우와 연중(7월)에 채용·퇴사한 경우로 범위를 보여 드립니다. 연중에 채용하면 그해 늘어난 인원이 절반만 잡히고 나머지는 다음 해 증가분으로 잡혀, 연중 기준이 더 크게 나올 수도 있습니다.'+(b.reg==='unk'?' 사업장 위치를 모름으로 고르셔서 수도권·지방 공제 단가 차이도 범위에 들어 있습니다.':''));
        else if(b.reg==='unk') K.push('사업장 위치를 모름으로 고르셔서 수도권·지방 공제 단가 차이를 범위로 보여 드립니다.');
        if(r.firstU) K.push('최초 창업 여부를 모르셔서, 사업을 넘겨받은 경우를 생각해 개업한 해에 늘어난 직원 몫을 뺀 금액을 최소로 잡았습니다.'); if(r.bookU) K.push('신고 방식을 모르셔서 최소 금액은 0원으로 잡았습니다. 장부 없이(추계) 신고한 해는 고용 공제를 받을 수 없습니다.'); if(r.etc) K.push('유흥주점 등 소비성서비스업은 고용 공제 대상이 아니어서, 업종은 상담에서 확인합니다.');   /* 2026.10.27 재검토 */ if(r.firstN) K.push('사업을 넘겨받았거나 법인으로 바꾼 경우에는 전 사업자의 직원 수와 비교해야 해서, 개업한 해에 늘어난 직원 몫은 계산하지 않았습니다. 1차 검토 때 서류로 확인합니다.'); else if(r.firstQ) K.push('개인사업자를 법인으로 바꿨거나 사업을 넘겨받은 경우에는 개업한 해에 늘어난 직원 몫이 달라질 수 있어, 1차 검토 때 서류로 확인합니다.');   /* 2026.10.27 */ if(r.pre19) K.push('2019년 이전에 늘어난 직원이 있으면 2021년에도 공제(3년 차)가 남아 있을 수 있습니다. 이 부분은 계산하지 않고, 1차 검토 때 신고서 등 서류를 받아 직접 확인합니다.');   /* 2026.10.27 태형: 꼬이는 건 서류로 */ if(r.noBase0) K.push('2019년 말 직원 수를 비워 두셔서 2020년에 늘어난 직원의 2021~2022년 공제는 계산하지 않았습니다.'); if(r.socIns) K.push('2020~2022년에 늘어난 직원은 사회보험료 세액공제도 함께 받을 수 있는지 상담에서 확인합니다.'); if(r.noBase) K.push('2020년 말 직원 수를 비워 두셔서 2021년에 늘어난 직원 몫은 계산하지 않았습니다.');   /* 2026.10.26 */ if(J.why3) K.push(J.why3.trim()); if(r.jbSkip) K.push('직원이 줄어 다시 내야 할 공제(추징)가 공제액보다 큰 경우에는 고용 공제를 신청하지 않는 쪽이 유리해, 그 경우는 고용 공제 없이 계산했습니다(최소 금액).'); if(!r.jbDrop) K.push('공제받은 뒤 2년 안에 직원 수가 줄면 공제받은 세금을 다시 낼 수도 있습니다.');
        J.why=''; J.why2=''; J.why3='';
        J.extra='<ul class="cr-key">'+K.map(function(x){return '<li>'+x+'</li>';}).join('')+'</ul><details class="cr-more"><summary>계산 기준 자세히 보기</summary><p>2021~2022년에 늘어난 직원은 고용증대세액공제(중소기업 청년 등 수도권 1,100만 원·지방 1,200만~1,300만 원, 그 외 700만 원·770만 원), 2023~2025년에 늘어난 직원은 통합고용세액공제 기준으로 계산했습니다. 2023~2024년에 늘어난 직원은 두 제도 중 하나를 고를 수 있는데, 중소기업은 통합고용세액공제가 더 커서 통합고용세액공제로 계산했습니다.</p><p>고용증대세액공제의 청년은 29세 이하, 통합고용세액공제의 청년은 34세 이하라 기준이 다릅니다. 2023년부터는 29세 기준 청년 수를 알 수 없어, 2021~2022년에 늘어난 청년의 추가 공제와 2023년 청년 증가 인원은 범위로 보여 드립니다. 2019년 이전에 늘어난 직원 몫과 사회보험료 세액공제는 계산하지 않았습니다.</p><p>공제 단가는 중소기업 기준입니다(중견기업은 단가가 더 낮습니다). 2021년에 수도권 밖에서 늘어난 청년은 1,300만 원이 적용될 수도 있지만, 보수적으로 1,200만 원으로 계산했습니다.</p><p>창업감면·중소기업 특별세액감면에는 농어촌특별세가 붙지 않습니다.</p></details>'; }
      if(b.late==='part'||b.late==='u'){ ['st','sp'].forEach(function(k){ var it=r.items[k]; if(it.lv==='hi'){ it.lv='chk'; } if(it.lv!=='no') it.why2='기한 후에 신고한 해는 창업감면·중소기업 특별세액감면을 받을 수 없어, 늦게 신고한 해가 있으면 그해는 빠집니다(조세특례제한법 제128조제2항). 어느 해인지 몰라 최소 금액은 0원으로 잡았습니다.'; }); }
      var rule='<p class="cr-why">사업용계좌를 신고해야 하는데 안 했거나, 현금영수증 가맹 의무를 지키지 않은 해는 감면을 받을 수 없을 수도 있습니다(조세특례제한법 제128조제4항).</p>';
      if(r.items.st.lv!=='no') r.items.st.why=(r.items.st.why||'');
      html+='<h3>'+kindNm+'</h3><p class="cr-why">아래 항목별 금액은 한도를 적용하기 전 금액입니다. 실제로 돌려받으실 수도 있는 금액은 맨 위 합계와 \'연도별로 보기\'를 보세요.</p>'+card('창업중소기업 세액감면',r.items.st,r.items.st.lv!=='no'?rule:'',1)+card('중소기업 특별세액감면',r.items.sp,((r.items.st.lv!=='off'&&r.items.st.lv!=='no')?'<p class="cr-why">창업감면과 같은 해에는 큰 쪽 하나만 받을 수 있어, 합계에는 큰 쪽만 더했습니다.</p>':'')+'<p class="cr-why">작은 사업장(소기업) 기준입니다.</p>'+(Object.keys(b.rows).some(function(k){return (b.rows[k].rev||0)>100000})?'<p class="cr-why">매출이 큰 사업장은 업종별 소기업 기준을 넘으면 감면율이 더 낮거나(지방 5~15%) 수도권에서는 받지 못할 수도 있어, 매출이 10억 원을 넘는 해는 최소 금액을 0원으로, 120억 원을 넘는 해는 최대 금액도 낮은 감면율(중기업 기준)로 잡았습니다.</p>':''),1)+card('고용증대·통합고용세액공제',r.items.jb, (r.items.jb.extra||'')+(r.items.jb.lv!=='no'? '<div class="cr-warn"><b>직원 수에서 제외되는 사람(반드시 확인해 주세요)</b><ul><li>대표자 본인·배우자와 그 친족, 임원</li><li>근로계약기간 1년 미만인 근로자(계약 갱신으로 1년 이상이면 포함합니다)</li><li>월 소정근로시간 60시간 미만인 단시간근로자(60시간 이상은 0.5명, 요건 충족 시 0.75명으로 계산합니다)</li><li>근로소득 원천징수·국민연금·건강보험 납부 내역이 확인되지 않는 사람</li><li>청년 중 기간제·단시간·파견 근로자(청년 등 인원에서 제외합니다)</li></ul><p>사업을 넘겨받으면서 같이 넘어온 직원은 늘어난 것으로 보지 않습니다. 장부 없이(추계) 신고해 첫해에 공제받을 수 없었다면 2·3년 차에도 받을 수 없습니다(국세청 서면-2025-소득-4384). 근로계약서·4대보험·급여대장으로 상담에서 다시 셉니다.</p></div>':''),1);
      ['st','sp','jb'].forEach(function(k){ if(b.gotI&&b.gotI[k]) html+=gotCard(k); }); if(b.gotI&&b.gotI.st&&b.gotI.sp) html+=BOTH;
      var yt='<table class="cr-yt"><tr><th>연도</th><th>납부세액</th><th>감면액</th><th>고용 공제액</th><th>환급 예상액</th><th>청구 가능기한</th></tr>';
      Object.keys(r.years).forEach(function(t){ var y=r.years[t]; yt+='<tr><td>'+t+'</td><td>'+man(y.tax)+'</td><td>'+rng(y.red[0],y.red[1])+'</td><td>'+rng(y.job[0],y.job[1])+(y.claw[1]>0.5?'<br><small>추징 '+rngN(y.claw[0],y.claw[1])+'</small>':'')+(y.nt[1]>0.5?'<br><small>농어촌특별세 '+rngN(y.nt[0],y.nt[1])+'</small>':'')+'</td><td><b>'+rngS(y.sum[0],y.sum[1])+'</b>'+(y.over?'<br><small>'+'납부세액·최저한세 한도까지만 반영'+'</small>':'')+'</td><td>'+dl(b.kind,+t)+'</td></tr>'; });
      if(Object.keys(r.years).some(function(t){return r.years[t].sum[0]<-0.5})) html+='<p class="cr-note">어느 해는 다시 내야 할 공제(추징)가 그 해 공제보다 커서, 그 해만 보면 세금을 더 낼 수도 있습니다(연도별로 보기에서 (-)로 표시). 맨 위 합계는 여러 해를 합친 금액입니다.</p>';
      html+='<details class="how cr-det"><summary>연도별로 보기</summary>'+yt+'</table><p class="hint">청구 가능기한은 원래 신고기한부터 5년입니다. 성실신고확인 대상은 개인사업자 6월 30일, 법인 4월 30일로 늘어납니다.</p></details>';
      if(r.total[1]>0) html+='<p class="cr-note">최소한 내야 하는 세금(최저한세: 개인은 사업소득 산출세액의 35~45%, 법인은 과세표준의 7%)을 대략 빼고 계산했습니다. 창업감면 100%인 해는 최저한세가 없습니다. 한도를 넘는 고용 공제는 다음 해로 넘어갈 수도 있지만, 창업감면·중소기업 특별세액감면은 넘는 부분이 없어집니다.</p>';
      if(b.got!=='n') html+='<p class="cr-note">신고할 때 감면·공제를 이미 받으셨다면, 받은 만큼은 빠지고 차액만 돌려받을 수 있습니다.</p>';
      if(r.total[1]>0) html+='<p class="cr-note">비용을 빼고 실제 납부세액을 기준으로 대략 계산했습니다.'+(b.kind==='p'?' 근로·임대 등 다른 소득이 함께 있었다면 사업소득 몫만 감면돼 금액이 줄어들 수도 있습니다.':'')+'</p>';
      /* 2026.10.27 재검토(2차): 숨겨진 칸·고르지 않은 항목은 접수 메모에서 뺌('눌러서 선택'·NaN 방지) */
      var tv=function(id){ var e=$(id), lb=e&&e.closest('label'); if(!e||!String(e.value).trim()||(lb&&lb.hidden)) return ''; return txt(id); };
      memo.push('['+kindNm+'] '+['개업 '+b.open.y+'.'+b.open.m, tv('crInd'), tv('crReg'), b.sel.st?'처음 소득: '+(b.firstInc||'개업한 해'):'', tv('crFirst')?'최초 창업: '+tv('crFirst'):'', tv('crAge')?'창업 나이 '+b.age+'(군 '+b.mil+'개월)':'', tv('crBook'), tv('crLate')?'기한: '+tv('crLate'):'', tv('crGot')?'감면: '+tv('crGot'):''].filter(Boolean).join(' · ')+(checked('crt').indexOf('p')>=0&&checked('crt').indexOf('c')>=0?' · (개인사업자·법인사업자 둘 다 체크)':''));
      Object.keys(b.rows).forEach(function(t){ var x=b.rows[t]; memo.push(t+': '+[x.rev!=null?'매출 '+won(x.rev):'', '세금 '+won(x.tax), b.sel.jb?'직원 청년 '+x.y+'/그 외 '+x.o:''].filter(Boolean).join(' · ')); });
      var ir=function(nm,it){ return (!it||it.lv==='off')?'':nm+' '+(it.lv==='no'?'해당 없음':(it.max>0?rng(it.min,it.max):'확인 필요')); };
      memo.push('결과: '+[ir('창업감면',r.items.st), ir('중특감',r.items.sp), ir('고용 공제',r.items.jb), '납부세액 한도 합계 '+rng(r.total[0],r.total[1])].filter(Boolean).join(' · '));
    }
    if(o.bizGot){ html+='<h3>'+(o.bizGot.kind==='c'?'법인사업자':'개인사업자')+'</h3>'; ['st','sp','jb'].forEach(function(k){ if(o.bizGot.got[k]) html+=gotCard(k); }); if(o.bizGot.got.st&&o.bizGot.got.sp) html+=BOTH; memo.push('[사업자] 이미 받음: '+['st','sp','jb'].filter(function(k){return o.bizGot.got[k]}).map(function(k){return GOTNM[k]}).join('·')+' → 추가 검토 요청'); }
    if(o.workGot){ html+='<h3>근로자</h3>'; ['dep','rent','sme'].forEach(function(k){ if(o.workGot[k]) html+=gotCard(k); }); memo.push('[근로자] 이미 받음: '+['dep','rent','sme'].filter(function(k){return o.workGot[k]}).map(function(k){return GOTNM[k]}).join('·')+' → 추가 검토 요청'); }
    if(o.work){ var w=C.worker(o.work); tot[0]+=w.total[0]; tot[1]+=w.total[1];
      var capd=Object.keys(w.years).some(function(t){return w.years[t].capped});
      var dep={lv:w.dep[1]>0?'hi':'no', min:w.dep[0], max:w.dep[1], why: w.dep[1]>0?(capd?'넣으신 납부세액(결정세액)까지만 돌려받을 수 있어 그 한도로 맞췄습니다. ':'')+'세율은 총급여 구간으로 대략 잡았습니다. '+(Object.keys(w.years).some(function(t){return w.years[t].smeSh})?'중소기업 취업자 감면을 받는 해는 세금 대부분이 감면돼 부양가족 공제 효과가 줄어, 그만큼 낮게 잡았습니다. ':'')+'부모님 소득·나이 요건과 형제 중복 여부는 상담에서 확인합니다.':(Object.keys(o.work.rows).some(function(k){var x=o.work.rows[k];return x.par>0&&x.paid===0})?'결정세액이 0원인 해는 이미 낼 세금이 없어 돌려받을 금액이 없습니다':'빠뜨린 부모님을 넣지 않으셨습니다')};   /* 2026.10.27 재검토 */
      var anyNo=Object.keys(w.years).some(function(t){return w.years[t].rentNo});
      var rent={lv:w.rent[1]>0?'hi':'no', min:w.rent[0], max:w.rent[1], why: w.rent[1]>0?'월세 공제를 받으면 표준세액공제 13만 원은 받지 못해, 보험료·의료비 등 다른 공제가 없던 분은 13만 원 적게 잡았습니다(범위의 아래쪽). 무주택 세대주, 주택 규모·기준시가, 전입 요건은 상담에서 확인합니다.':(anyNo?'총급여 기준을 넘는 해는 월세 공제를 받을 수 없습니다':(Object.keys(o.work.rows).some(function(k){return o.work.rows[k].rent>0})?(Object.keys(o.work.rows).some(function(k){var x=o.work.rows[k];return x.rent>0&&x.paid===0})?'결정세액이 0원인 해는 이미 낼 세금이 없어 돌려받을 금액이 없습니다':'넣으신 납부세액(결정세액)이 부양가족 공제로 이미 다 차서 월세 몫은 0원으로 잡았습니다'):'월세를 넣지 않으셨습니다'))};
      if(!o.work.sel.dep) dep={lv:'off'}; if(!o.work.sel.rent) rent={lv:'off'};
      var S=o.work.sme, sme={lv:'off'};   /* 2026.11.02 중소기업 취업자 감면 */
      if(o.work.sel.sme&&S){ var sEnd=S.y*12+(S.m-1)+(S.kind==='o'?36:60), sOld=sEnd<2021*12;
        sme={lv:w.sme[1]>0?((S.kind==='u'||S.ind==='u'||S.req!=='never')?'chk':'hi'):'no', min:w.sme[0], max:w.sme[1],
          why: w.sme[1]>0? '결정세액에 감면율(청년 90%, 그 외 70%)을 곱하고 연 한도(2022년분까지 150만 원, 2023년분부터 200만 원) 안에서 대략 계산했습니다. 한도에 걸리는 해는 근로소득세액공제가 같이 줄어드는 몫을 빼고 낮게 잡았습니다.'+(S.kind==='u'?' 대상을 모르셔서 70%·3년인 경우와 90%·5년인 경우를 범위로 보여 드립니다.':'')+(S.req==='mid'?' 회사에 신청한 해는 그해 연말정산 때 1년 전체에 반영됐을 수 있어, 그 전 해만 계산했습니다.':S.req==='unk'?' 회사가 신청했는지 모르셔서 최소 금액은 0원으로 잡았습니다.':'')+(S.ind==='u'?' 회사 업종을 모르셔서 최소 금액은 0원으로 잡았습니다.':'') : (S.ind==='no'?'병원·의원, 법무·회계·세무, 금융·보험, 일반 학원, 공공기관 등은 대상 업종이 아닙니다.':sOld?'감면 기간(취업일부터 5년, 청년이 아니면 3년)이 2021년 전에 끝났습니다.':'넣으신 해 중 감면 기간 안에서 아직 받지 않은 해가 없거나, 결정세액이 0원입니다.'),
          why2: w.sme[1]>0? (S.quit?'퇴사하셨어도 회사 협조 없이 주소지 세무서에 직접 신청(경정청구)할 수 있습니다.':'다니는 중이면 회사(원천징수의무자)를 통해 다시 정산하는 방식으로 진행합니다.')+' 회사 업종(대상 업종이 정해져 있음), 대표의 가족·임원 여부, 청년 나이(군 복무 기간 차감)는 상담에서 확인합니다.' : ''}; }
      html+='<h3>근로자</h3>'+card('부양가족 공제',dep)+card('월세 세액공제',rent)+card('중소기업 취업자 소득세 감면',sme)+(Object.keys(w.years).some(function(t){return w.years[t].unk})?'<p class="cr-note">납부세액(결정세액)을 비워 두신 해는 최소 금액을 0원으로 잡았습니다. 결정세액이 0원이면 돌려받을 세금이 없습니다.</p>':''); ['dep','rent','sme'].forEach(function(k){ if(o.work.gotI[k]) html+=gotCard(k); });
      var wsS=o.work.sel.sme, yt2='<table class="cr-yt"><tr><th>연도</th><th>부양가족 공제액</th><th>월세 공제액</th>'+(wsS?'<th>중소기업 취업자 감면액</th>':'')+'<th>환급 예상액</th><th>청구 가능기한</th></tr>';
      Object.keys(w.years).forEach(function(t){ var y=w.years[t]; yt2+='<tr><td>'+t+'</td><td>'+rng(y.dep[0],y.dep[1])+'</td><td>'+(y.rentNo?'총급여 기준 초과':rng(y.rent[0],y.rent[1]))+'</td>'+(wsS?'<td>'+rng(y.sme[0],y.sme[1])+'</td>':'')+'<td><b>'+rng(y.sum[0],y.sum[1])+'</b></td><td>'+dl('w',+t)+'</td></tr>'; });
      html+='<details class="how cr-det"><summary>연도별로 보기</summary>'+yt2+'</table></details>';
      Object.keys(o.work.rows).forEach(function(t){ var x=o.work.rows[t]; memo.push('[근로자] '+t+': 총급여 '+({a:'5,500 이하',b:'5,500 초과~7천 이하',c:'7천 초과~8천 이하',d:'8천 초과'})[x.g]+' · 결정세액 '+(x.paid>=0?won(x.paid):'모름')+' · 빠뜨린 부모 '+x.par+'(70세 이상 '+Math.min(x.old,x.par)+') · 월세 월 '+won(x.rent)); });
      if(o.work.sel.sme&&S) memo.push('[근로자] 중소기업 취업자: '+({y:'청년',o:'60세 이상·장애인·경력단절',u:'대상 모름'})[S.kind]+' · 취업 '+(S.y<=2015?'2015년 이전':S.y+'.'+S.m)+' · 업종 '+({ok:'대상 업종',no:'대상 아님',u:'모름'})[S.ind]+' · 감면 신청 '+({never:'안 함',mid:S.ry+'년부터',unk:'모름'})[S.req]+' · '+(S.quit?'퇴사':'재직 중'));
      memo.push('결과: '+[o.work.sel.dep?'부양가족 '+rng(w.dep[0],w.dep[1]):'', o.work.sel.rent?'월세 '+rng(w.rent[0],w.rent[1]):'', o.work.sel.sme?'중소기업 취업자 감면 '+rng(w.sme[0],w.sme[1]):''].filter(Boolean).join(' · '));
    }
    // 2026.10.26 태형: 개업 연도에 연동 — 넣은 해만 표시(예: 2023년 개업이면 2023~2025년분)
    var YS=[].concat(o.biz&&o.biz.rows?Object.keys(o.biz.rows):[], o.work&&o.work.rows?Object.keys(o.work.rows):[]).map(Number).filter(function(x){return x>=2021&&x<=2025;}), y1=YS.length?Math.min.apply(null,YS):2021, y2=YS.length?Math.max.apply(null,YS):2025;
    var SPAN=y1===y2? y1+'년분' : y1+'~'+y2+'년분', LAWT=y1===y2? y1+'년에 시행되던 법 기준으로 계산했습니다.' : y1+'~'+y2+'년 각 해에 시행되던 법 기준으로 계산했습니다.';
    var head='<div class="cr-top"><p class="r-label">'+SPAN+' 돌려받으실 수도 있는 세금 (예상 범위·참고용)</p><p class="big">'+(tot[1]>0?rng(tot[0],tot[1]):((o.biz||o.work)?'이 입력으로는 확인된 금액이 없습니다':'세무사 검토로 확인합니다'))+'</p>'+
      '<p class="r-sub">'+(tot[1]>0?((o.biz&&o.biz.kind==='c'&&!o.work)?'법인지방소득세는 따로 확인합니다. ':'개인지방소득세(소득세의 10%)도 별도로 함께 돌려받으실 수도 있습니다'+((o.biz&&o.biz.kind==='c')?'(법인지방소득세는 따로 확인). ':'. '))+LAWT:((o.biz||o.work)?'이 입력으로는 해당 항목이 보이지 않습니다. 그래도 접수된 내용으로 한 번 더 확인해 드립니다.':'이미 받으신 항목은 금액을 계산하지 않고, 더 받을 수 있는지 세무사가 검토해 연락드립니다.'))+'</p></div>';
    var foot='<div class="cr-foot"><p>1차 검토는 무료입니다. 계산기로 나온 예상 금액을 재검토하며, 경정청구 가능성을 검토해드립니다. 정확한 세액 계산은 경정청구 진행 시 산정이 가능합니다.</p><div class="cr-submit"><button type="button" class="btn primary" id="crSend">1차 무료 검토 접수하기</button><p class="cr-ok" id="crSent" role="status" hidden></p></div><p class="hint">검토에 필요하면 지난 신고서(최소 5년~최대 7년 치)를 요청드릴 수 있습니다.</p><p class="hint">해당하지 않으면 그대로 말씀드립니다. 청구 기한이 가장 먼저 끝나는 것은 '+y1+'년분입니다(근로자·법인사업자는 개인사업자보다 빠를 수 있음).</p></div>';
    $('crOut').innerHTML=head+html+foot; $('crOut').hidden=false; if($('crOut').scrollIntoView) $('crOut').scrollIntoView({behavior:'smooth',block:'start'});
    memo.unshift('확인 항목: '+['st','sp','jb','dep','rent','sme'].filter(function(k){return mode(k)}).map(function(k){return GOTNM[k]+'('+({none:'안 받음',got:'받음',unk:'모름'})[mode(k)]+')'}).join(', '));
    memo.unshift('예상 범위 합계: '+rng(tot[0],tot[1]));
    // 2026.10.26 태형: 결과 보기와 1차 무료 검토 접수를 나눔(관심 없는 분까지 접수되면 연락 부담) — 접수는 버튼을 눌러야만 전송
    lastMemo=memo.join('\n'); if($('crSend')) $('crSend').addEventListener('click',function(){ submitNow(); });   /* 2026.10.27 재검토: 입력을 바꾼 뒤 눌러도 다시 계산해서 보냄 */ if(io&&$('crSend')) io.observe($('crSend')); upd();
  }
  function send(text){
    var el=$('crSent');
    if(text===sentKey){ el.textContent='1차 무료 검토가 접수되었습니다. 확인 후 연락드리겠습니다.'; return; }
    if(!LEAD.action){ el.textContent='접수 연결을 준비 중입니다. 전화나 카카오톡으로 연락해 주세요.'; el.className='cr-ok err'; return; }
    var d=new FormData();
    d.append(LEAD.service,(LEAD.tag||'')+'경정청구 (납부세액 환급 검토) · 경정청구 확인 계산기에서'+(sentKey&&sentKey!==text?' (수정)':''));
    d.append(LEAD.name,$('crName').value.trim()); d.append(LEAD.phone,$('crPhone').value.trim());
    if(LEAD.time) d.append(LEAD.time,'상관없음'); if(LEAD.memo) d.append(LEAD.memo,text.slice(0,1900)); if(LEAD.agree) d.append(LEAD.agree,'동의');
    window.__claimLast=text;
    if(window.__claimNoSend){ sentKey=text; el.textContent='(미리보기) 실제 접수는 보내지 않았습니다.'; upd(); return; }
    if(sending===text) return;   // 2026.10.23 재검토: 응답을 기다리는 동안 여러 번 눌러도 한 번만
    var prev=sentKey; sending=text; sentKey=text; $('crSend').disabled=true;
    fetch(LEAD.action,{method:'POST',mode:'no-cors',body:d}).then(function(){ sending=''; $('crSend').disabled=false; el.textContent='1차 무료 검토가 접수되었습니다. 확인 후 연락드리겠습니다.'; el.className='cr-ok'; upd(); })
      .catch(function(){ sending=''; sentKey=prev; $('crSend').disabled=false; el.textContent='접수하지 못했습니다. 잠시 뒤 다시 누르시거나 전화·카카오톡으로 연락해 주세요.'; el.className='cr-ok err'; });
  }
  $('crGo').addEventListener('click',run);
  // 2026.10.26 태형: 결과 보기 옆에 1차 무료 검토 접수 버튼 + 결과를 내려 볼 때 화면 아래에 접수 버튼이 따라오게
  $('crGo').insertAdjacentHTML('afterend',' <button type="button" class="btn primary" id="crGo2">1차 무료 검토 접수</button>');
  var stk=document.createElement('div'); stk.className='cr-sticky'; stk.id='crSticky'; stk.hidden=true;
  stk.innerHTML='<span>입력하신 내용으로 1차 무료 검토를 신청하실 수 있습니다.</span><button type="button" class="btn primary" id="crGo3">1차 무료 검토 접수</button>'; document.body.appendChild(stk);
  var vis={go:false,send:false};
  function upd(){ var done=!!sentKey && sentKey===lastMemo; stk.hidden = done || !lastMemo || $('crOut').hidden || vis.go || vis.send; }
  var io=('IntersectionObserver' in window)? new IntersectionObserver(function(es){ es.forEach(function(e){ vis[e.target.id==='crGoBox'?'go':'send']=e.isIntersecting; }); upd(); }) : null;
  if(io) io.observe($('crGoBox'));
  function submitNow(){ if(!infoOk()){ var em=$('crSent')||$('crGoMsg'); if(em){ em.hidden=false; em.textContent='성함·연락처와 개인정보 동의(맨 위 1단계)를 확인해 주셔야 접수할 수 있습니다.'; if(em.id==='crSent') em.className='cr-ok err'; } return; }   /* 2026.10.27 재검토(2차): 동의를 풀고 누르면 안내 */
    run(); if(!lastMemo || $('crOut').hidden) return; $('crSent').hidden=false; send(lastMemo); }
  $('crGo2').addEventListener('click',submitNow); $('crGo3').addEventListener('click',submitNow);
  function stale(){ var out=$('crOut'); if(out.hidden || $('crStale')) return; var p=document.createElement('p'); p.id='crStale'; p.className='cr-ok err'; p.textContent='입력이 바뀌었습니다. 결과 보기를 다시 눌러 주세요. 아래는 바뀌기 전 결과입니다.'; out.insertBefore(p,out.firstChild); [].forEach.call(out.children,function(c){ if(c!==p && !c.classList.contains('cr-foot')) c.style.opacity='.45'; }); }   /* 2026.10.27 재검토(2차): 이전 결과는 흐리게 */
  $('cr').addEventListener('input',stale,true); $('cr').addEventListener('change',stale,true);
  lock();
})();
