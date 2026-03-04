import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import textwrap, os

df_main   = pd.read_csv('data/processed/master_tourism_analysis.csv')
prov_list = pd.read_csv('data/processed/ProvinceThailandList.csv')

name_map = {
    'Chai Nat':'Chainat','Lop Buri':'Lopburi','Sing Buri':'Singburi',
    'Prachin Buri':'Prachinburi','Nong Bua Lam Phu':'Nong Bua Lamphu',
    'Si Sa Ket':'Si Saket','Suphan Buri':'Suphanburi',
    'Sa Kaeo':'Sra Kaeo','Buriram':'Buri Ram'
}
df_main['ProvinceEN']   = df_main['ProvinceEN'].str.strip().replace(name_map)
prov_list['ProvinceEN'] = prov_list['ProvinceEN'].str.strip().replace(name_map)

df_agg = df_main.groupby('ProvinceEN').agg({'total_visitors':'mean','real_revenue':'mean'}).reset_index()
sec_base = prov_list[prov_list['City_type_EN'].str.contains('Secondary', na=False, case=False)].copy()
sec = pd.merge(sec_base[['ProvinceEN','Region_EN']], df_agg, on='ProvinceEN', how='left').fillna(0)
sec['yield_per_head']   = (sec['real_revenue']*1e6) / sec['total_visitors'].replace(0,1)
sec['contribution_pct'] = (sec['real_revenue'] / sec['real_revenue'].sum()) * 100
valid = sec[sec['total_visitors']>0]
x_mid, y_mid = valid['yield_per_head'].median(), valid['contribution_pct'].median()

def classify(row):
    if row['total_visitors']==0: return 'EMERGING'
    hy,hc = row['yield_per_head']>=x_mid, row['contribution_pct']>=y_mid
    if hy and hc:     return 'STARS'
    if not hy and hc: return 'MASS MARKET'
    if hy and not hc: return 'PREMIUM NICHE'
    return 'EMERGING'
sec['Quadrant'] = sec.apply(classify, axis=1)

QUADS = ['STARS','PREMIUM NICHE','MASS MARKET','EMERGING']
QUAD_COLOR = {'STARS':'#2471A3','PREMIUM NICHE':'#7D3C98','MASS MARKET':'#BA4A00','EMERGING':'#5D6D7E'}
WRAP_CHARS=44; LH_P=0.200; LH_R=0.165; GAP_R=0.13; HDR_H=0.62; IPAD=0.24; PTOP=0.18; PBOT=0.18

def get_regions(q):
    qd = sec[sec['Quadrant']==q]
    return [(r.upper(), ', '.join(qd[qd['Region_EN']==r]['ProvinceEN'].sort_values().tolist()))
            for r in sorted(qd['Region_EN'].unique())]

def measure_h(q):
    t=0
    for _,pt in get_regions(q):
        t += LH_R + LH_P*len(textwrap.wrap(pt,WRAP_CHARS)) + GAP_R
    return t

def card_h(q): return HDR_H + measure_h(q) + PTOP + PBOT

FIG_W=14.0; MARGIN=0.45; GAP=0.30; ROW_GAP=0.28
CARD_W = (FIG_W - MARGIN*2 - GAP)/2
ROW1_H = max(card_h(q) for q in ['STARS','PREMIUM NICHE'])
ROW2_H = max(card_h(q) for q in ['MASS MARKET','EMERGING'])
Y2=0.38; Y1=Y2+ROW2_H+ROW_GAP
FIG_H = Y1+ROW1_H+1.05+0.15
XL=MARGIN; XR=MARGIN+CARD_W+GAP

COORDS={'STARS':(XL,Y1,CARD_W,ROW1_H),'PREMIUM NICHE':(XR,Y1,CARD_W,ROW1_H),
        'MASS MARKET':(XL,Y2,CARD_W,ROW2_H),'EMERGING':(XR,Y2,CARD_W,ROW2_H)}

fig = plt.figure(figsize=(FIG_W,FIG_H), facecolor='#F8F9FA')
ax  = fig.add_axes([0,0,1,1])
ax.set_xlim(0,FIG_W); ax.set_ylim(0,FIG_H); ax.axis('off'); ax.set_facecolor('#F8F9FA')

def T(x,y,s,**kw): ax.text(x,y,s,transform=ax.transData,**kw)
def HL(x0,x1,y,c,lw=1,a=1): ax.plot([x0,x1],[y,y],color=c,lw=lw,alpha=a,transform=ax.transData,solid_capstyle='round')
def CARD(x,y,w,h,ct):
    ax.add_patch(mpatches.FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.06',facecolor='white',edgecolor='#E0E4E8',linewidth=1.2,transform=ax.transData,zorder=1))
    ax.add_patch(mpatches.FancyBboxPatch((x,y+h-0.08),w,0.08,boxstyle='round,pad=0.02',facecolor=ct,edgecolor='none',transform=ax.transData,zorder=2))

T(FIG_W/2,FIG_H-0.30,'STRATEGIC PORTFOLIO OF 55 SECONDARY CITIES',ha='center',va='top',fontsize=15,fontweight='bold',color='#1A252F')
T(FIG_W/2,FIG_H-0.60,'Classification based on Median Efficiency (Yield) and Market Share (% Revenue)',ha='center',va='top',fontsize=9,color='#95A5A6')
HL(0.5,FIG_W-0.5,FIG_H-0.82,'#DDE1E4',lw=1)

for q in QUADS:
    cx,cy,cw,ch = COORDS[q]
    color=QUAD_COLOR[q]; count=len(sec[sec['Quadrant']==q]); regions=get_regions(q)
    CARD(cx,cy,cw,ch,color)
    hy=cy+ch-0.30
    T(cx+IPAD,hy,q,ha='left',va='top',fontsize=12,fontweight='bold',color=color,zorder=3)
    T(cx+cw-IPAD,hy,f'{count} Cities',ha='right',va='top',fontsize=9.5,color='#B2BEC3',zorder=3)
    dy=hy-0.30; HL(cx+IPAD,cx+cw-IPAD,dy,color,lw=1.2,a=0.25)
    yc=dy-PTOP
    for rl,pt in regions:
        wl=textwrap.wrap(pt,WRAP_CHARS)
        T(cx+IPAD,yc,rl,ha='left',va='top',fontsize=7.5,fontweight='bold',color='#A8B2BC',zorder=3); yc-=LH_R
        for ln in wl:
            T(cx+IPAD,yc,ln,ha='left',va='top',fontsize=10.5,color='#2C3E50',zorder=3); yc-=LH_P
        yc-=GAP_R

T(FIG_W/2,0.18,'Source: Thailand Tourism Statistics  ·  Classified by yield per visitor vs. revenue contribution median',
  ha='center',va='bottom',fontsize=8,color='#C0C7CE')

os.makedirs('visualizations',exist_ok=True)
plt.savefig('visualizations/Figure_9_Strategic_Summary.png',dpi=150,bbox_inches='tight',pad_inches=0.1,facecolor='#F8F9FA')
plt.close()
print("Done")