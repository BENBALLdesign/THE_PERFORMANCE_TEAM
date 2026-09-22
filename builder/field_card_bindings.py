"""Authored claim-to-source selections, reviewed against SG-010's actual rows.

Each semicolon group binds ONE card row (label + detail) to compact-guide rows.
The last group binds the qualification. Titles/cues are editorial navigation;
their context is the union of the selected facts, not a new claim of evidence.
"""

ALIASES={'m':'method','f':'foundation_water','l':'load_paths','v':'movement',
         'r':'roof_structure','w':'walls','o':'openings','s':'site_decks',
         'g':'garage','c':'roof_cover','p':'water','d':'dwv','h':'water_heat',
         'a':'gas','e':'service','b':'circuits','x':'devices','t':'gas_heat','i':'oil_heat'}

# Stable source IDs are resolved from row labels; these reviewed indices are
# frozen to those labels in review-lock.json before rendering is allowed.
BINDINGS=[
 'm0;m0;m0;m1;m0',
 'c5;c5 s3;s3;c5;c5',
 's3;s3;s3;s3;s3',
 's3;s3;m1 m3',
 's5;s5;s5;s5;s5',
 's4;s4;s4',
 's3;w4;s3;m3;m3 w0',
 'm3;m3;m3;m4;m2',
 'w0;w0 v2;w0',
 'w1;w1;w1;w1;w1',
 'w2;w2;w2;w2 v2;w2',
 'w3;w3;w3;w3;w3',
 'w5;w5;w5;w5;w5',
 'o3;o3;o3',
 's0;s1;s0;s1',
 's2;s2;s2',
 'g0;g0;g0;g0;g0',
 'g1;o5 g1;g1',
 'g2;g2;h3 g2;g2',
 'g3;g3;g3;g3;g3',
 'g4;g4;g4 g5',
 'g3;g5;g5;g5;g5',
 'x1;x1;x1 e2;m3;x3',
 's3;o3;o3;m1;f1 m1',
 'f1 f2;l0;e0 t1;m1 m4;m0 m3',
 'f1;f1;p1;f1',
 'f3;f3;f3',
 'l0 l5;l0;l0;l5;l1',
 'l0;l0;l0;f4;l0',
 'f0;f5 v0;f0;f5;f5',
 'd4;d4;d4 d5',
 'i1;i1;i1;i1',
 't1;t1;t0 t4 i2',
 'a0;a0 a2;a0;a2',
 'h0;h0;h0;h3;h0',
 'h1 h2;h1;h2',
 'i0;i0;i2 i3;i4;i0',
 'e3;x0 e3;x0;x0;e5 b5',
 'e0;e2;e2;m3 e1;e1 e2',
 'e0;x4;x4;x4 m3;x4',
 'v3;v3;v3;v3;v0 v5',
 'v0;v0;v0;v0 v5;v0',
 'o0;o0;o0;o0;o0',
 'o2;o2;p1 o2;o2',
 'o5;o5;o1',
 's2;s2;s2;s2',
 'x3;x3;x3;x3;x3',
 'm1;m1 m3;m4;m5',
 'p0;d0 d3;d1;h1 d0 d4',
 'd0;d0;d0;d0',
 'p1;p1;p1',
 'd1;d1;d1',
 'p4;d1;p4',
 'p2;p2;p2 d3;p2;p2',
 'h5;h5;h5;h5;h5',
 'd0 d3;d3;d3 m3;d3',
 'c0;c0;m3;m3;c0 m3',
 'r0;r0;r1;r1',
 'r0;r0;r0',
 'r3;r3;r3',
 'c1;r2;r2 c1',
 'c2;c2;c5;c2 w1;c2',
 'c3;c3;r4;r4;c3',
 'c4;c4;c4;c4;c4',
]

# Footnote selection is editorial and explicit. These qualify the card; they
# are not invented inline evidence or a claim that every source has that note.
NOTES=[
 '03 05 09','03','02','03','03','03','03','03',
 '03','03','03','03','03','03','03','02 03',
 '03','03','02','03','03 06','03 06','03 06','03',
 '03 06','03 06','02 03','03','03','03','03 06','03 05',
 '03 06','03','02 05','02 03','03','03 06','02 03','03',
 '03','03','03','03','03','02 03','03 06','03 09',
 '03','03 06','03','03','03','03','02 06','03',
 '03','03','03','03','03 05','03','03','03',
]

# Exact APP-D labels, intentionally chosen. These are related definitions;
# display aliases do not create a second definition or imply source bolding.
TERMS={
 1:['Home inspection / code compliance'],2:['Grade / retaining wall'],
 3:['Grade / retaining wall'],4:['Grade / retaining wall'],5:['Grade / retaining wall'],
 9:['Veneer','WRB'],10:['Step / counter / kick-out flashing'],
 11:['Veneer','Weep / drainage plane'],12:['EIFS'],13:['Fascia / soffit / frieze','Rake / eave'],
 14:['Sash / glazing / IGU'],15:['Ledger / guard / handrail','Load path'],16:['Ledger / guard / handrail'],
 19:['FVIR'],23:['GFCI','AFCI'],25:['Load path','Footing / foundation'],
 26:['Efflorescence','Capillary action'],27:['Flood opening / air vent','Vapor retarder'],
 28:['Bearing / connection','Load path','Joist / beam / girder'],29:['Bearing / connection'],
 30:['Post-tensioned slab'],31:['DWV'],33:['Heat exchanger','CO','Gravity / forced air'],
 34:['CSST','Grounding / bonding'],36:['T&P / TPR'],37:['Draft hood / barometric damper'],
 38:['Grounding / bonding','GFCI','AFCI'],39:['AWG','Grounding / bonding'],
 41:['Differential movement'],42:['Differential movement'],43:['Sash / glazing / IGU'],
 44:['Sash / glazing / IGU'],46:['Ledger / guard / handrail'],47:['GFCI','AFCI'],
 49:['DWV','Trap / vent','T&P / TPR'],50:['Functional flow / drainage'],
 52:['Trap / vent'],53:['Cross-connection / air gap'],54:['DWV'],
 56:['Functional flow / drainage'],58:['Rafter / truss'],59:['Collar tie / rafter tie'],
 60:['Vapor retarder'],62:['Step / counter / kick-out flashing'],63:['DWV'],
}

assert len(BINDINGS)==len(NOTES)==64
