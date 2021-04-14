import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

# Load data
df = pd.DataFrame({"Resp" : [0.23270873986795, 2.73352379542056, 5.41701963104684, 4.19905375172031, 5.27566539441751, 2.64610579761599, 4.85896583872851, 3.1366868660496, 6.05109041801408, 2.8608768798204, 1.01958319265222, 0.169743140683567, 1.85500176108768, 2.96953443835347, 3.03174807693735, 4.51695377981097, -0.472145317562387, 3.81752960323056, 3.87578688808113, 8.28592101666275, 1.71028957102144, 1.45434281092976, 3.16771648742703, 3.59184236535871, 0.621846689778215, 3.15309818158441, 2.3186960338454, 3.27770141982383, 2.51467940451471, 1.08582175832488, 2.53129436572075, 2.30277109244019, 2.31204884147311, 1.99039769266874, 1.60211718683673, 0.395170191974176, -0.356526253135392, 1.51050586351969, -0.58367979126414, 4.25721149274905, -0.392953848358245, 2.89717164954219, 2.68687134906104, 4.39111380863853, 1.54909247275772, 0.906078338895643, -0.699130053805078, 0.361540598981517, -0.849863357495101, 3.38356266102915, 1.96184856611151, 2.89369562625057, 0.925762054618639, 0.154526638508218, -0.41781590793083, -0.104886457325833, 3.87765763391801, 0.182670302864808, -3.07409417473651, 3.80204083552492, -0.67256609535997, 2.88968063414333, -1.39742975207015, 7.00548838976163, -3.43066544409698, 3.13906752375131, 4.88399653012171, 4.71969427526232, -0.135366672629913, 0.439801760090428, -1.19138278075859, 2.52040063568745, 2.23797352851077, 7.52309174575423, 6.35822076795745, 4.66406078948089, 4.97407562521116, 1.83125389925885, 3.81153842894517, 1.74439787786031, 6.57207394135645, 1.45512036989413, 3.12805686170747, 4.48060226752095, 0.979695596904267, 5.14234198025476, 2.35660289211518, 5.68555137376919, 1.10345391888349, 3.60369511326788, 5.62616792526944, 7.73900212237369, 3.20666472385802, 1.7119223306992, 2.47018328096971, 5.86975866775598, 1.62385484515661, 3.66029107379396, 7.60740441360481, 2.93041132091012, 6.92085049341582, 5.66186660884622, 5.66186660884622, 3.86475698217864, 9.43762888230549, 0.572516315887168, 4.66013034134497, 0.983810225407773, 2.62411041435887, 5.10554252634404, 2.73694179091159, 4.86787874727794, 0.885912314394534, 2.65920926116195, 9.41643840922984, 4.41479152657266, 5.53697629475504, 1.64105186439889, 1.97299979973252, 4.69870284057265, 3.46377858095294, 7.30091244462851, 7.23390550999326, 2.80588618652646, 8.16018025962343, 3.37868092811112, 7.41707361432165, 3.46897145418195, 7.23518102798418, 3.12291684648875, 3.99291956260239, 3.13925082963552, 3.96577936463676, 5.19114261446854, 2.87899238360707, 6.29469257936956, 0.709638214519791, 4.75223006946849, 8.4530042521172, 9.28216905347651, 7.5023316522265, 2.6500368522832, 3.22164069279669, 6.7646898662473, 4.33944934925846, 4.93522116048779, 7.52538543646276, 2.38097084960012, 5.77212720652635, -0.0322300712334918, 6.51736982610648, 2.27588626166095, 8.31080994676906, -0.0654169420110409, 3.36225924166874, -1.76443628058812, 1.31677738475381, 4.46909632192405, 2.47988222357978, 2.69942724070711, 5.66186660884622, 2.31211141878609, 7.57505008151006, 6.82200037158074, 7.06778944045353, 2.80670106101841, 2.83572250866148, 1.66299267705144, 1.18635168051454, 8.31169013986513, 6.13727092978409, 4.28214417168448, 4.54212057853112, 1.23682625583246, 3.7314228201582, 4.87730764550183, 5.80446970799172, 3.32595637064972, 1.04593728024589, 1.67072903826624, -0.104428883530835, 6.99964842569835, 0.225345352780135, 6.3297557160805, 1.08177616837876, 7.02453769060748, 5.37315002120473, 7.58275874114681, 2.35900934280984, 2.06695319544844, -0.482195895912738, 4.05924249063952, 5.67845604130633, 5.84069711751763, 8.24337196825062, 7.60032222859827, 7.78641764974115, 3.21691912486215, 9.68952348517883, 2.51650025391148, 9.78141175148797, 5.19498818683087, 5.53992457779455, 3.66260397437098, 4.62166887593008, 5.18618485261108, 5.74200420486626, 5.66186660884622, 6.4940258450692, 7.18465747589612, 9.48320668151633, 9.14751882749382, 6.75894893343008, 3.69310004097642, 5.02016140215193, 6.10183718601544, 3.90157801208706, 6.81479020873631, 3.78037760834775, 3.06967107982601, 3.4539398281995, 5.66186660884622, 4.28196315346565, 3.15801343922462, 5.66186660884622, 2.11785296747231, 1.50132891804956, 5.66186660884622, 4.23542747402016, 5.79497051467914, 1.28460923414295, 3.60296044319748, 0.834112116666402, 3.58560322335707, 4.83447335702296, 7.2337009237665, 3.47505930154787, 2.54627142644041, 0.54138294087547, 4.2186517935395, -0.697127274847685, 7.66768851341194, 6.65776726816031, 5.27954009202925, 3.15183786116167, 1.05295195917279, 6.91856389920738, 2.01861409593044, 7.00463423733137, 3.55876476091441, 2.45122128573605, 1.88600609685201, 1.94853940514349, 5.86130599845327, 4.48964256541618, 6.30051131967997, 3.26498418694174, 5.00841474154028, 7.31907627478094, 5.20155121655558, 5.28025202022659, 1.82103786221895, 3.80776115671624, 5.74695894701355, 1.54684889514809, 4.90226910501857, 4.05520138507984, 6.24065928033851, 4.54802314411247, 4.09996204143789, 4.82063352646422, 3.47536021970628, 6.80039784498549, 4.75601251010573, 2.41240857569427, 2.102590406067, 3.25498774757671, 4.68194792316995, 0.533615976008016, 4.49411260462914, -0.402122342426437, 5.20227476882042, 5.6283883985811, 7.00035091502944, 1.81167429093048, 1.67152669931232, 2.11213337634675, 2.60745144792257, 1.3613907181648, 2.71015883484275, 2.78233833151957, 3.38945827447892, 4.08815366551599, 1.96058548625414, 5.66186660884622, 0.660955360835042, 4.5246734700856, -0.93706823331657, 0.744207784697149, 0.423879229538759, 1.55609145015348, 3.26712272098704, 1.60076159274637, 2.87680289308126, 1.8796672722067, 1.86711458276715, 3.79540646077909, 7.96768999388583, 2.00280294235959, 1.93612840377384, 1.12561743614662, 1.57916885051281, 1.19756310235235, 5.47322900368074, 4.44387739624714, 5.66186660884622, 4.41072478009717, 0.837142586214851, 1.72844263450828, 4.3986788233925, 4.46228372447355, 0.693314089510964, 1.06917401566064, 2.30215481954687, 3.73057429931281, 4.21896437094588, 1.08094345386883, 4.04997432318125, 0.271446777273966, 5.89613896753606, 6.39256603329658, 5.66186660884622, 4.31772135655154, 3.61488711740196, 1.61457860942571, 3.59429229519863, 3.36774444952195, 5.27019011250326, 4.01310524722076, 6.15042860029013, 4.49591191169745, -0.502386280894906, 5.52936352466774, 2.49213574661321, 3.85806119043768, 1.01855864709157, 1.45274454281458, 2.13880547781208, 0.408133327890197, 4.05565030127871, 5.66186660884622, 4.40954647666781, -0.190845812966522, 3.55613360326472, 4.85286229017113, 8.66620000270406, 4.43127739465707, 1.71979129317007, -0.505322066067553, 4.32111912426832, 4.09497258348059, 7.41023155898559, 8.13454669765071, 3.99171693701958, 7.2149764901128, 4.30193492105495, 7.75560006903865, 4.83451356458387, 7.38838354304857, 5.40207308251431, 2.1498065057534, 4.62851627889316, 3.26150112546597, 5.34507105255723, 5.53495691900585, 6.32379417059595, 1.03237358854034, 6.7390784764668, 8.33277202871304, 10.07426714552, 6.30202791773945, 3.27322693231385, 4.06954156926305, 5.42955773861381, 2.03409461095623, 5.30665342237358, 6.01804079157278, 4.77436640801994, 4.19320354810689, 3.25164706656657, 2.58567558778046, 5.66186660884622, 6.41123551861481, 2.12971051764184, 2.91685897272325, 1.2505643027353, 3.03025205510962, 3.67150324223828, 3.71734979888157, 6.99183873702479, 2.15872415213235, 1.93919444815755, 6.83338647403178, 7.51540246585984, 3.08640350549442, 3.12075434982201, 5.66186660884622, 4.6279885974216, 2.05594241806808, 5.94398928501848, 5.30388757720566, 5.48459991325172, 2.51910480254259, 2.74285247230514, 3.48272507047333, 5.66186660884622, 5.11744411390119, 1.3206453958714, 0.555397284167376, 4.20103964682266, 1.4221667082422, 5.7926174455516, 0.853533911435112, 5.8579236406527, 0.388309580117256, 3.57626101219238, 5.97278789840145, 7.9861054741627, 3.84049980435593, 3.42434479126202, 0.18251908811337, 5.66298510722615, 4.24503835741481, 4.24224072350478, 7.62497587274308, 4.70244890431751, 7.5817964065099, 1.82080525308595, 6.05973311036299, 1.48449303975891, 6.68733955333795, 0.926025073516443, 2.20535589264442, 5.66186660884622, 3.76818723634019, 6.17871957298159, 3.89049390232024, 4.37904450868106, 1.80694792367694, 3.27396481570887, 6.1517719685817, 7.43602946016178, 4.27678626771961, 0.769061716747804, 1.35746124107566, 5.11473661226829, 3.71837971297898, 2.76606404355941, 5.89586495328465, 3.93072763928619, 5.18783484758563, -0.118228313020603, 6.94151373553571, 0.577957241682736, 6.77051286450493, 0.326922499869483, 2.71371074795014, 1.61274501223277, 2.77804495915593, 5.51923164388028, 4.18560131812356, 2.8420550674565, 2.60959264932911, 5.93336357455345, 9.158448520012, 5.98923270745117, 6.75760373622399, 2.16813823116732, 1.58706081438007, 2.30861493191536, 1.04636424429101, 4.44641010896311, 4.83644309554558, 2.17472078287978, 4.17897647310683, 0.880174556960651, 5.66186660884622, 0.44863613870394, 5.75566504628875, -0.637663237529383, 3.99054887897076, 2.08715988393856, 0.684648518503455, 2.87289782704466, 5.10569640554218, 3.39436492214943, 1.6922260365594, 3.21608497495837, 7.16535346024746, 5.75947972321416, 4.67650115310647, 0.61059334826797, 2.13893991137785, 2.51762811881338, 4.28192396921435, 6.12130040237518, 7.34021449132779, 5.66186660884622, 7.55395048805781, 7.33033711494981, 4.76623046727661, 5.33390004136583, 7.45444469835812, 2.03102439762214, 3.76830415409593, 2.76649629453707, 4.47266968813825, 4.86247597421131, 5.93635153225727, 7.36015574599773, 1.57495621636644, 8.05248793163726, 8.09078176236051, 6.01909300979898, 7.13978262845677, 3.89117075174632, -0.644081602296078, 7.85868184861432, 1.38093984732549, 3.24365115645723, 4.16446390028776, 3.56733010003735, 3.93382797479304, 1.53743280237089, 4.85130693215718, 5.63697701328942, 7.48151257012849, 1.61394263883143, 0.0899674994912868, 2.22746554939216, -0.516696002083212, 4.98803994132123, 1.15061999955306, 5.66186660884622, 2.03003025717754, 4.10288879339466, 3.46269851952092, 5.8019050617784, 5.60911001614403, 2.53381986217593, 0.814757728338399, 1.74248676342286, 3.4556847761566, 5.57738894961144, 7.97477181235198, 5.05385768494132, 7.03352091434064, 3.56785366671071, 6.34527931130784, 5.66186660884622, 6.04861137125595, 1.72075864833456, 2.48434178150305, 3.30421529937439, 2.95292592290583, 5.84007187807131, 5.04483770559986, 7.8533676405095, 1.741822587751, 6.25166036148916, 7.35287197800398, 8.71398328874721, 5.60650343364321, 3.68473814307379, 2.3072354165659, 2.27791585932574],"Cond" : [-0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5],"SubjID" : [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24],"SubjID" : [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 23, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24],"Cond" : [-0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5],"ItemID" : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]})
# Specify model that Tisane inferred
model = sm.MixedLM.from_formula(formula="Resp ~ Cond",vc_formula = {"SubjID" : "0 + C(SubjID)" , "ItemID" : "0 + C(ItemID)"},re_formula = "1 + Cond",groups = "SubjID",data=df)

# Fit/run model, see output
results = model.fit()
print(results.summary())
