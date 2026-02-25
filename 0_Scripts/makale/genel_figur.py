import graphviz
import os

def create_clean_dashboard():
    os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin'
    dot = graphviz.Digraph('Metabolitics_Design', format='pdf')
    
    dot.attr(rankdir='TB', nodesep='0.5', ranksep='0.6', fontname='Helvetica', splines='none')
    dot.attr('node', shape='box', style='rounded,filled', fontname='Helvetica', margin='0.3,0.25', fontsize='12', color='none')
    dot.attr('edge', style='invis') 

    # Ana Baslik
    dot.node('Title', 
             'Metabolitics Benchmarking Framework: The 7-Dimensional Experimental Space\nTotal Unique Configurations: N = 57,600', 
             fillcolor='#2C3E50', fontcolor='white', fontsize='16', fontname='Helvetica-Bold')

    # --- A. Biyolojik Baglam ---
    with dot.subgraph(name='cluster_bio') as c:
        c.attr(style='rounded', bgcolor='#EBF5FB', color='#85C1E9', penwidth='2', margin='20')
        c.attr(label='A. Biological Context', fontname='Helvetica-Bold', fontcolor='#21618C', fontsize='14')
        c.node('D1', '1. Datasets (6)\nBC, BRCA, PRAD, PDAC, Alzheimer, Diabetes', fillcolor='#AED6F6', fontcolor='#154360')
        c.node('D3', '3. Resolutions (6)\nReaction, Pathway (Min, Max, Mean, Median, Sum)', fillcolor='#AED6F6', fontcolor='#154360')
        c.edge('D1', 'D3')

    # --- B. Modelleme Cekirdegi ---
    with dot.subgraph(name='cluster_model') as c:
        c.attr(style='rounded', bgcolor='#E9F7EF', color='#7DCEA0', penwidth='2', margin='20')
        c.attr(label='B. Modeling Core', fontname='Helvetica-Bold', fontcolor='#1E8449', fontsize='14')
        c.node('D2', '2. Objectives (20)\nBaseline, Topology, Local (k1-6), Robust (\u03C3), ATP, Biomass', fillcolor='#A9DFBF', fontcolor='#145A32')
        c.node('D4', '4. Input Types (2)\nFlux Only, Flux + Coefficients (Cr)', fillcolor='#A9DFBF', fontcolor='#145A32')
        c.edge('D2', 'D4')

    # --- C. Makine Ogrenmesi ---
    with dot.subgraph(name='cluster_ml') as c:
        c.attr(style='rounded', bgcolor='#FDEDEC', color='#F1948A', penwidth='2', margin='20')
        c.attr(label='C. Machine Learning Engine', fontname='Helvetica-Bold', fontcolor='#943126', fontsize='14')
        c.node('D5', '5. ML Models (4)\nRandom Forest, XGBoost, Logistic Reg., Linear SVM', fillcolor='#F5B7B1', fontcolor='#641E16')
        c.node('D6', '6. Selectors (2)\nANOVA (Parametric), Wilcoxon (Non-Parametric)', fillcolor='#F5B7B1', fontcolor='#641E16')
        c.node('D7', '7. Densities (5)\n10%, 20%, 50%, p<0.05, Full (100%)', fillcolor='#F5B7B1', fontcolor='#641E16')
        c.edge('D5', 'D6')
        c.edge('D6', 'D7')

    # Ana basliktan kolonlarin tepesine gorunmez bag atarak dogal hizalama sagliyoruz
    dot.edge('Title', 'D1')
    dot.edge('Title', 'D2')
    dot.edge('Title', 'D5')

    dot.render('Figure1_ExperimentalDesign', view=True, cleanup=True)
    print("Hatasiz PDF olusturuldu.")

if __name__ == '__main__':
    create_clean_dashboard()