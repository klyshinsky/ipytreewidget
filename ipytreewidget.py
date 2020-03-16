# Tree Widget for Jupyter Notebook
# Eduard Klyshinsky, 2020

from ipywidgets import HTML
from IPython import get_ipython

# this is source code of widget.

""" 
TreeWidget class accepts a Python dictionary/list and draws a tree in Jupyther notebook.
Uses HTML widget from ipywidgets. All nodes and hints are collapsable.
A tree is a node or list of nodes.
A node is a dictionary containing string keys associated with proper values:
text - text label for a node.
hint - extra information connected to a node.
childs - list of nodes.
text-color, text-bkcolor - color of the text and background of a node. Use HTML colors here.
hint-color, hint-bkcolor - color of the hint's text and background of a node. Use HTML colors here.
"""
class TreeWidget:
    # Node Id
    _freeId = 1
    
    # Adds a script for collapsing nodes and hints to the notebook.
    get_ipython().run_cell_magic("html","", """<script>
var timer;
    
function showHideTree(ide, prefix, ida){
    if(document.getElementById(ida).innerHTML=="▼") {
      document.getElementById(ide).style.display=prefix+"block";
      document.getElementById(ida).innerHTML="▲";}
    else if(document.getElementById(ida).innerHTML=="▲") {
      document.getElementById(ide).style.display="none";
      document.getElementById(ida).innerHTML="▼";}
     
    if(document.getElementById(ida).innerHTML=="►") {
      document.getElementById(ide).style.display="inline-block";
      document.getElementById(ida).innerHTML="◄";}
    else if(document.getElementById(ida).innerHTML=="◄") {
      document.getElementById(ide).style.display="none";
      document.getElementById(ida).innerHTML="►";}
}

function expandTree(element, display, prefix){
  if( element.id.substr(0,4)=="tlim" ) {
    var s = element.id.substr(0,3)+'a'+element.id.substr(4,20)
    showHideTree(element.id, prefix, s);
  }
  
  for(var i=0; i<element.children.length; i++) {
    if(element.children[i].id[3]=='m' || element.children[i].id[3]=='a'|| element.children[i].id=="")
      expandTree(element.children[i], display, prefix);
  }  
}

function doubleClickTree(ide, prefix, ida){
  if (timer) clearTimeout(timer);
  
  if(document.getElementById(ida).innerHTML=="▼") 
    expandTree(document.getElementById(ide), prefix+"block", prefix)
  else if(document.getElementById(ida).innerHTML=="▲")
    expandTree(document.getElementById(ide), "none", "")
}
</script>
""")
    
    """ Default constructor.
    """
    def __init__(self):
        self.data = None
    
    """ Generates HTML code for a tree. I don't want to use any extra libraries here.
    """
    def _generateHTML(self, data):
        # Tree is a collapsable list.
        html = '<ul style="list-style-type:none; margin-left:-25px; line-height:1.5">'
        for node in data:
            html += '<li>'
            text = str(node.get('text', ''))
            
            # If there is any childs - add an arrow for folding/unfolding the branch.
            cur_id = -1
            childs_count = len(node.get("childs", []))
            if childs_count != 0:
                cur_id = TreeWidget._freeId
                TreeWidget._freeId += 1
                click = 'if(timer)clearTimeout(timer);timer=setTimeout(function(){showHideTree("tlim'+\
                        str(cur_id)+'", "", "tlia'+str(cur_id)+'");}, 250);'
                html += f'''<a nohref onclick='{click}' 
                    ondblclick='doubleClickTree("tlim{cur_id}", "", "tlia{cur_id}");' 
                    style="text-decoration:none; color:black">
                    <div id="tlia{cur_id}" style="display:inline-block;margin-right:5px">▼</div></a>\n'''
            else:
                html += f'<div style="display:inline-block;margin-right:5px;opacity:0">▼</div>\n'
            textbkcolor = node.get("text-bkcolor", "#FFFFFF")
            textcolor = node.get("text-color", "#000000")
            # A kind of callback for clicking on the node. 
            # Currently you cannot do any output here, just calculations.
            if "onclick" in node.keys():
                onclick = f'onclick="IPython.notebook.kernel.execute(\'{node["onclick"]}\')"'
            else:
                onclick = ""
            # Adds the node's label.
            html += f'<div style="display:inline-block; background-color:{textbkcolor}; color:{textcolor};padding-left:2px;padding-right:2px" {onclick}>'+ \
                    text+'</div>'
            # Adds collapsable hnt if any. With an arrow to collapse.
            hint = node.get('hint', '')
            if hint != "":
                if cur_id == -1:
                    cur_id = TreeWidget._freeId
                    TreeWidget._freeId += 1
                    
                hintbkcolor = node.get("hint-bkcolor", "#FFFFFF")
                hintcolor = node.get("hint-color", "#000000")
                html += f'<a nohref onclick=\'showHideTree("tlib{cur_id}", "inline-", "tlic{cur_id}");\' style="text-decoration:none; color:black"><div id="tlic{cur_id}" style="display:inline-block;margin-left:5px">►</div></a>\n'
                html += f'<div style="display:none; background-color:{hintbkcolor}; color:{hintcolor};padding-left:2px;padding-right:2px" id="tlib{cur_id}">{hint}</div>\n'
            # Final code for the case if we have any children.
            if childs_count != 0:
                html += f'<div style="display:none" id="tlim{cur_id}">\n'
                html += self._generateHTML(node["childs"])
                html +='</div>'
        html += "</ul>"
        return html        
        
    """ Accepts a dictionary, generates an HTML page and draws it.
        A tree is a node or list of nodes.
        A node is a dictionary containing string keys associated with proper values:
        text - text label for a node.
        hint - extra information connected to a node.
        childs - list of nodes.
        text-color, text-bkcolor - color of the text and background of a node. Use HTML colors here.
        hint-color, hint-bkcolor - color of the hint's text and background of a node. Use HTML colors here.
        
        Parameters.
        data - drawn tree.
        header - text of the header. Not drawn if header==None.
        footer - text of the footer. Not drawn if footer==None.
    """
    def show(self, data, header=None, footer=None):
        # We accepting list and dict only!
        if data != None:
            if type(data) is dict:
                self.data = [data]
            elif type(data) is list:
                self.data = data
            else:
                display(HTML("<b>You should pass either list or dictionary!</b>"))
                return
            
        # Draw a border. Need to be moved to properties.
        html = '<div style="border: 1px solid #DDDDDD">'
        if header != None:
            html += f'<div style="width:100%;background-color:#DDDDDD;padding-left:8px;line-height:1.5">{header}</div>'
        html += self._generateHTML(self.data)
        html += '</div>'
        if footer != None:
            html += f'<div style="width:100%;background-color:#DDDDDD;padding-left:8px;line-height:1.5">{footer}</div>'
            
        # Generates and draws an HTML page.
        page = HTML()
        page.value = html
        display(page)