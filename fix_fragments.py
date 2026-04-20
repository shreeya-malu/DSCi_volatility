import codecs
import sys

def main():
    try:
        lines = codecs.open('dashboard.py', 'r', 'utf-8').readlines()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    out = []
    tab_idx = None

    for line in lines:
        stripped = line.strip()
        
        if stripped.startswith('# ============================================================================'):
            if tab_idx is not None:
                out.append(f"        render_{tab_idx}()\n\n")
                tab_idx = None
                
        if stripped == 'with tab2:':
            out.append(line)
            out.append("        @st.fragment\n")
            out.append("        def render_tab2():\n")
            tab_idx = 'tab2'
            continue
        elif stripped == 'with tab3:':
            out.append(line)
            out.append("        @st.fragment\n")
            out.append("        def render_tab3():\n")
            tab_idx = 'tab3'
            continue
        elif stripped == 'with tab4:':
            out.append(line)
            out.append("        @st.fragment\n")
            out.append("        def render_tab4():\n")
            tab_idx = 'tab4'
            continue
        elif stripped == 'with tab5:':
            if tab_idx is not None:
                out.append(f"        render_{tab_idx}()\n\n")
                tab_idx = None
            out.append(line)
            continue
            
        if tab_idx is not None:
            if line.strip() == '':
                out.append(line)
            else:
                out.append('    ' + line)
        else:
            out.append(line)

    if tab_idx is not None:
        out.append(f"        render_{tab_idx}()\n\n")

    try:
        codecs.open('dashboard.py', 'w', 'utf-8').writelines(out)
        print("Successfully updated dashboard.py")
    except Exception as e:
        print(f"Error writing file: {e}")

if __name__ == "__main__":
    main()
