qss='''
/*Copyright (c) DevSec Studio. All rights reserved.

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/




/*-----QLabel-----*/
QLabel
{
	font-weight: bold;
	font-family: Arial;
	font-size: 9;
	/* border: 1px solid black; */
	/* background-color: white; */
	/* color: #fff; */
}

/*----QPushButton----*/
QPushButton {
	font-weight: bold; font-family: Arial;
    background-color: #e1e1e1;
    
    border-style: solid; border-width: 1px;
    border-radius: 10px; border-color: grey;
    padding: 4px;
}
QPushButton:hover {
    background-color: #CCCCCC;
}

QPushButton:pressed {
    background-color: #B8B8B8;

}

 

QWidget{
	font-family: Arial;
	font-size: 12px;

}
/*-----QTabBar-----*/
QTabBar
{
	font-family: Arial; font-size: 12px;
	font-weight: bold;
}

/* headers... */
/* 
QHeaderView::section {
	font-family: Arial; font-weight: bold;
    background-color: #e1e1e1; padding: 4px;
    font-size: 12px; border-style: none;
    border-bottom: 1px solid #fffff8;
    border-right: 1px solid #fffff8;
}  */
QHeaderView::section {
	font-family: Arial; font-weight: bold;
    background-color: #4899AD; padding: 4px;
    /* 4b6858 */
    color:white;
    font-size: 12px; border-style: none;
    border-bottom: 1px solid #fffff8;
    border-right: 1px solid #fffff8;
    
} 
/* QHeaderView::section {
	font: 12pt Cambria Math; font-weight: bold;
    color:white;
    height:50px;
    background-color:#4899AD; 
    padding:2px;
    
} */

/* table widget */
QTableWidget{
    font: 12pt "Cambria Math";
    border-radius:5px;
    border: 2px solid grey;
}

QTableWidget::item:selected{
    background-color:#CDE8FF;
    color:black;
}



#controlTableWidget::item:!focus {
    background-color:white;
    color:black;
}
#tableWidget { 
    font-size: 13pt;
   
}


/* list widget */

QListWidget {
    border-radius:5px;
    border: 2px solid grey;
    padding: 4px;
    background-color: white;
    font:"Cambria Math";
    font-size: 12pt;

}

#tokens::item:!focus{
    background-color:white;
    color:black;
}

#proudction_listWidget::item:!focus{
    background-color:white;
    color:black;
}





/* items */


QTableView::item:focus
{
   selection-background-color: grey;
}

QTableView::item
{
   selection-background-color: grey;
}

/* QTextEdit */

/* QTextEdit{
   font: 15pt "Times New Roman";
    font-family: Arial; 
} */
/* QTextEdit:editable{
    font: 15pt "Times New Roman";
}    */

/* QLineEdit */

QLineEdit, QLineEdit:hover {
    border: none; padding-bottom: 2px;
    border-bottom: 1px solid #dddddd; color: #111111;
    background-color:rgba(0,0,0,0);
}

QLineEdit:editable{
    border: none; padding-bottom: 2px;
    border-bottom: 2px solid #b2dfdb; font: 12pt "Cambria Math";
}

QLineEdit:disabled{
    border: 0px solid white; padding-bottom: 2px;
    border-bottom: 2px solid #eeeeee;
}

QLineEdit:focus{
    border: 0px solid white; padding-bottom: 2px;
    border-bottom: 2px solid #00695c; color: #111111;
} 
QLineEdit:pressed {
    border: none; padding-bottom: 2px;
    border-bottom: 2px solid #00695c;
}

/* ------- specific elements style declaration ------- */

/* tabWigets */

#tabMain QTabBar::tab
{
    background-color: #4b6858; height: 40px; 
    color: white; width: 200px;
}      
#tabMain QTabBar::tab:last {border-top-right-radius: 40px;}

#tabMain QTabBar::tab:first {border-top-left-radius: 40px;}

#tabMain QTabBar::tab:selected 
{
    background-color: #4899AD;
    /* #357180 */
}

#tabMain QTabBar::tab:selected:hover{
    background-color:#4899AD;
}

#tabMain QTabBar:tab:hover{
    background-color: #222F28;
}


#tabLexic QTabBar::tab
{
    background-color: #4b6858; height: 30px; 
    color: white; width: 180px;
} 

#tabLexic QTabBar::tab:last {border-top-right-radius: 20px;}

#tabLexic QTabBar::tab:first {border-top-left-radius: 20px;}

#tabLexic QTabBar::tab:selected {background-color: #4899AD;}


#tabSyntactic QTabBar::tab
{
    background-color: #4b6858; height: 180px;
    color: white; width: 20px;
}
#tabSyntactic QTabBar::tab:selected{background-color: #4899AD;}

#tabSyntactic QTabBar::tab:disabled{background-color: #cccccc;}

#tabSyntactic QTabBar::tab:last {border-bottom-left-radius: 20px;}

#tabSyntactic QTabBar::tab:first {border-top-left-radius: 20px;}

#tabErrores QTabBar::tab
{
    background-color: #4b6858; height: 30px; 
    color: white; width: 180px;
} 

#tabErrores QTabBar::tab:last {border-top-right-radius: 20px;border-bottom-left-radius:0px}

#tabErrores QTabBar::tab:first {border-top-left-radius: 20px;}


#tabProd QTabBar::tab
{
    background-color: #4b6858; height: 30px; 
    color: white; width: 180px;
} 

#tabProd QTabBar::tab:last {border-top-right-radius: 20px;border-bottom-left-radius:0px}

#tabProd QTabBar::tab:first {border-top-left-radius: 20px;}

/* tab labels */

#labelTitleFirst, #labelPATitle, #labelPA, #labelFCTitle, #labelFC, #labelExpFirst, 
#label_left_side, #label_right_side, #label_title_app, #label_application {
    border: 2px solid grey;
    padding: 4px;
    font:"Cambria Math";
}
#label_left_side, #label_right_side, #label_title_app, #labelTitleFirst { 
    margin-bottom: 10px; border-radius:5px; 
    color: white; background-color:#4899AD;
    font-weight: bold; 
}

#labelExpFirst, #label_item_left, #label_item_right,
#label_detail_1, #label_detail_2, #label_application, #label_explain_title {
    font:"Cambria Math";
    font-size: 12pt;
}

#suggestion_title_label, #info_title_label, #autors_label {
    margin-bottom: 10px; border-radius:5px; 
    color: white; background-color:#4899AD;
    font-weight: bold; padding:4px;
}

#labelPATitle {border-top-left-radius:10px; color: white; background-color:#4899AD; font-weight: bold;}
#labelPA {border-left:none;border-top-right-radius:10px;}
#labelFCTitle {border-top:none; border-bottom:none; color: white; background-color:#4899AD; font-weight: bold;}
#labelFC {border-top:none; border-bottom:none; border-left:none;}
#labelExpFirst {border-bottom-left-radius: 10px; border-bottom-right-radius:10px } 
#label_left_side {border-right:none; border-top-right-radius:0px; border-bottom-right-radius:0px} 
#label_right_side {border-top-left-radius:0px; border-bottom-left-radius:0px}
#label_application {border-radius:5px; height:100px; width:100px;}
#T_label {margin-top: 10px;}
#label_explain_title {font-size: 14pt; font-weight:bold; }
#label_detail_1, #label_detail_2 {font-weight:bold;}
#ErrorLogLabel {border-radius:5px; background:rgb(255, 255, 255); border: 2px solid grey; }
/* ##labelTitle{ ....} */

#conjuntoNameEdit, #conjuntoExpEdit, #tokenExpEdit, #tokenNameEdit, #nameEdit{
    font-size:14pt;
}


#NT_label, #T_label, #conjuntoLabel, #label_prodList_title {
    border-top-left-radius:10px;
    border-top-right-radius:10px;
    padding: 4px;
    font:"Cambria Math";
    font-size:10pt;
    font-weight: bold;
    color: white; background-color:#4899AD;

}

/* buttons */
/* #conjuntoAddButton, #conjuntoCreateButton, #tokenCreateButton */
#btn_CFirst, #btn_CSig, #btn_back, #btn_next, #delButtonEC, #btn_search
 { margin-top: 10px;}

#createBtn { margin-right:10px;}

/* Frames */
#frame_prod_items, #frame_prod_detail {
    border: 2px solid grey;
    padding: 4px;
    font:"Cambria Math";
    border-radius:5px; 

}
/* list widgets */
#NT_items, #tokens, #conjuntoList, #proudction_listWidget, #ErrorLogLabel {
    border-top: none;
    border-top-left-radius:0px;
    border-top-right-radius:0px;
}

#NT_items {
     margin-bottom: 10px;
}



/* central widget */
#centralwidget, #centralwidget_dialog {
    background-color: #ffffff;
}
'''