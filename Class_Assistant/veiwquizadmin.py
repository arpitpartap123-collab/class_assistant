"""Quiz activity for the admin, with a CSV export of the results."""
import csv
import tkinter.ttk as ttk
import tkinter.messagebox as msg
from tkinter.filedialog import asksaveasfilename
import customtkinter as ctk
from connection import connect

BG="#080D18"; CARD="#101827"; CARD2="#0B1422"; BORDER="#243650"; TEXT="#F8FAFC"; MUTED="#8EA0B8"
BLUE1="#2563EB"; BLUE2="#60A5FA"; GREEN1="#059669"; GREEN2="#34D399"; RED1="#DC2626"; RED2="#F87171"; PURPLE1="#7C3AED"; PURPLE2="#A78BFA"
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def setup_styles():
    style=ttk.Style()
    try: style.theme_use("clam")
    except Exception: pass
    style.configure("Quiz.Treeview",background=CARD2,foreground=TEXT,fieldbackground=CARD2,borderwidth=0,rowheight=42,font=("Segoe UI",11))
    style.configure("Quiz.Treeview.Heading",background="#172337",foreground="#E2E8F0",borderwidth=0,font=("Segoe UI",11,"bold"),padding=(10,10))
    style.map("Quiz.Treeview",background=[("selected",BLUE1)],foreground=[("selected","#FFFFFF")])
    style.configure("Quiz.Vertical.TScrollbar",background="#1A2A40",troughcolor=CARD2,bordercolor=CARD2,arrowcolor="#94A3B8")


class GradientButton(ctk.CTkFrame):
    def __init__(self,master,text,command,width=130,height=42,color1=BLUE1,color2=BLUE2):
        super().__init__(master,width=width,height=height,fg_color="transparent",corner_radius=12)
        self.command=command; self.text=text; self.w=width; self.h=height; self.c1=color1; self.c2=color2
        self.grid_propagate(False); self.pack_propagate(False)
        self.canvas=ctk.CTkCanvas(self,width=width,height=height,highlightthickness=0,bd=0,bg=BG)
        self.canvas.pack(fill="both",expand=True); self.draw(False)
        self.canvas.bind("<Enter>",lambda e:self.draw(True)); self.canvas.bind("<Leave>",lambda e:self.draw(False)); self.canvas.bind("<Button-1>",lambda e:command())
    def rgb(self,h):
        h=h.lstrip("#"); return tuple(int(h[i:i+2],16) for i in (0,2,4))
    def hx(self,v): return "#{:02x}{:02x}{:02x}".format(*v)
    def draw(self,hover):
        self.canvas.delete("all"); a=self.rgb(self.c2 if hover else self.c1); b=self.rgb(self.c1 if hover else self.c2)
        for x in range(self.w):
            t=x/max(self.w-1,1); col=self.hx(tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))); self.canvas.create_line(x,0,x,self.h,fill=col)
        self.canvas.create_text(self.w//2,self.h//2,text=self.text,fill="white",font=("Segoe UI",11,"bold"))


setup_styles()


class viewQuizAdmin:
    def __init__(self):
        self.root=ctk.CTkToplevel(); self.root.title("Quiz Activity"); self.root.configure(fg_color=BG); self.root.state("zoomed")
        self.conn=connect(); self.cr=self.conn.cursor()

        header=ctk.CTkFrame(self.root,fg_color=CARD,corner_radius=20,border_width=1,border_color=BORDER); header.pack(fill="x",padx=32,pady=(24,12))
        ctk.CTkLabel(header,text="QUIZ ACTIVITY",font=("Segoe UI",28,"bold"),text_color=BLUE2).pack(pady=(18,2))
        ctk.CTkLabel(header,text="Double click an attempt to view the complete answer sheet",font=("Segoe UI",12),text_color=MUTED).pack(pady=(0,18))

        bar=ctk.CTkFrame(self.root,fg_color=CARD,corner_radius=18,border_width=1,border_color=BORDER); bar.pack(fill="x",padx=32,pady=8)
        self.searchField=ctk.CTkEntry(bar,width=340,height=42,corner_radius=12,placeholder_text="Search student or lecture...",placeholder_text_color="#64748B",fg_color=CARD2,border_color="#30435E",text_color=TEXT,font=("Segoe UI",12)); self.searchField.grid(row=0,column=0,padx=(18,8),pady=16)
        GradientButton(bar,"Search",self.searchAttempts,115,42,BLUE1,BLUE2).grid(row=0,column=1,padx=7,pady=16)
        GradientButton(bar,"Refresh",self.refreshData,115,42,PURPLE1,PURPLE2).grid(row=0,column=2,padx=7,pady=16)
        GradientButton(bar,"Export to CSV",self.exportToCsv,145,42,GREEN1,GREEN2).grid(row=0,column=3,padx=7,pady=16)
        GradientButton(bar,"Delete Attempt",self.deleteAttempt,145,42,RED1,RED2).grid(row=0,column=4,padx=(7,18),pady=16)

        wrapper=ctk.CTkFrame(self.root,fg_color=CARD,corner_radius=20,border_width=1,border_color=BORDER); wrapper.pack(fill="both",expand=True,padx=32,pady=(8,28))
        tableFrame=ctk.CTkFrame(wrapper,fg_color=CARD2,corner_radius=14); tableFrame.pack(fill="both",expand=True,padx=14,pady=14)
        columns=("id","student","lecture","course","total","correct","score","on")
        self.table=ttk.Treeview(tableFrame,columns=columns,show="headings",style="Quiz.Treeview")
        for key,title,width in [("id","ID",60),("student","Student",200),("lecture","Lecture",260),("course","Course",140),("total","Questions",110),("correct","Correct",100),("score","Score %",110),("on","Attempted On",180)]:
            self.table.heading(key,text=title); self.table.column(key,width=width,anchor="center")
        scroll=ttk.Scrollbar(tableFrame,orient="vertical",command=self.table.yview,style="Quiz.Vertical.TScrollbar"); self.table.configure(yscrollcommand=scroll.set); scroll.pack(side="right",fill="y",pady=8); self.table.pack(fill="both",expand=True,padx=8,pady=8)
        self.table.bind("<Double-1>",self.openAnswerSheet); self.getAttempts(); self.root.protocol("WM_DELETE_WINDOW",self.closeWindow); self.root.mainloop()

    def query(self,keyword=None):
        base="""SELECT a.id, s.name, l.title, c.name, a.total_questions,
                         a.correct_answers, a.score, a.attempted_on
                  FROM quiz_attempts a
                  JOIN students s ON s.id = a.student_id
                  JOIN lectures l ON l.id = a.lecture_id
                  JOIN courses c ON c.id = l.course_id"""
        if keyword: self.cr.execute(base+" WHERE s.name LIKE %s OR l.title LIKE %s ORDER BY a.attempted_on DESC",(f"%{keyword}%",f"%{keyword}%"))
        else: self.cr.execute(base+" ORDER BY a.attempted_on DESC")
        return self.cr.fetchall()

    def getAttempts(self,keyword=None):
        for row in self.table.get_children(): self.table.delete(row)
        for record in self.query(keyword): self.table.insert("","end",values=record)

    def searchAttempts(self): self.getAttempts(self.searchField.get().strip())
    def refreshData(self): self.searchField.delete(0,"end"); self.getAttempts()

    def deleteAttempt(self):
        selected=self.table.selection()
        if not selected: msg.showwarning("Warning","Please select an attempt first",parent=self.root); return
        data=self.table.item(selected[0])["values"]
        if not msg.askyesno("Confirm","Delete this quiz attempt?",parent=self.root): return
        self.cr.execute("DELETE FROM quiz_attempts WHERE id = %s",(data[0],)); self.conn.commit(); msg.showinfo("Success","Attempt has been deleted",parent=self.root); self.refreshData()

    def exportToCsv(self):
        rows=self.query(self.searchField.get().strip() or None)
        if not rows: msg.showwarning("Warning","There is nothing to export",parent=self.root); return
        path=asksaveasfilename(parent=self.root,defaultextension=".csv",filetypes=[("CSV files","*.csv")],initialfile="quiz_activity.csv")
        if not path: return
        try:
            with open(path,"w",newline="",encoding="utf-8") as f:
                writer=csv.writer(f); writer.writerow(["Attempt ID","Student","Lecture","Course","Questions","Correct","Score %","Attempted On"]); writer.writerows(rows)
            msg.showinfo("Success",f"Exported {len(rows)} row/s to\n{path}",parent=self.root)
        except Exception as e: msg.showerror("Error",f"Could not write the file.\n\n{e}",parent=self.root)

    def openAnswerSheet(self,event):
        selected=self.table.selection()
        if not selected: return
        data=self.table.item(selected[0])["values"]; attemptId=data[0]
        sheet=ctk.CTkToplevel(); sheet.title("Answer Sheet"); sheet.configure(fg_color=BG); sheet.geometry("1100x720")
        header=ctk.CTkFrame(sheet,fg_color=CARD,corner_radius=20,border_width=1,border_color=BORDER); header.pack(fill="x",padx=28,pady=(22,12))
        ctk.CTkLabel(header,text="ANSWER SHEET",font=("Segoe UI",24,"bold"),text_color=BLUE2).pack(pady=(16,2)); ctk.CTkLabel(header,text=f"{data[1]}  •  {data[2]}",font=("Segoe UI",12),text_color=MUTED).pack(pady=(0,16))
        wrapper=ctk.CTkFrame(sheet,fg_color=CARD,corner_radius=20,border_width=1,border_color=BORDER); wrapper.pack(fill="both",expand=True,padx=28,pady=(6,24))
        tableFrame=ctk.CTkFrame(wrapper,fg_color=CARD2,corner_radius=14); tableFrame.pack(fill="both",expand=True,padx=12,pady=12)
        table=ttk.Treeview(tableFrame,columns=("type","question","given","correct","result","similarity"),show="headings",style="Quiz.Treeview")
        for key,title,width,anchor in [("type","Type",100,"center"),("question","Question",380,"w"),("given","Student Answer",200,"w"),("correct","Expected",200,"w"),("result","Result",90,"center"),("similarity","Similarity",100,"center")]: table.heading(key,text=title); table.column(key,width=width,anchor=anchor)
        scroll=ttk.Scrollbar(tableFrame,orient="vertical",command=table.yview,style="Quiz.Vertical.TScrollbar"); table.configure(yscrollcommand=scroll.set); scroll.pack(side="right",fill="y",pady=8); table.pack(fill="both",expand=True,padx=8,pady=8)
        q="""SELECT q.question_type, q.question_text, ans.student_answer,
                      q.correct_answer, ans.is_correct, ans.similarity_score
               FROM quiz_answers ans JOIN questions q ON q.id = ans.question_id
               WHERE ans.attempt_id = %s ORDER BY ans.id"""
        self.cr.execute(q,(attemptId,))
        for qtype,question,given,correct,is_correct,similarity in self.cr.fetchall(): table.insert("","end",values=(qtype,question,given or "-",correct,"Correct" if is_correct else "Wrong",f"{similarity:.3f}" if similarity is not None else "-"))

    def closeWindow(self):
        try: self.cr.close()
        except Exception: pass
        try: self.conn.close()
        except Exception: pass
        self.root.destroy()


if __name__ == "__main__":
    viewQuizAdmin()