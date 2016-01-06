import sqlite3
from openpyxl import Workbook
from collections import namedtuple, OrderedDict


class Reviewer():
    '''
    This Class captures the the data and operations required for performing post
    assessment analysis.
    '''
    def __init__(self, teaching_set, DBname):
        '''
        Grab ALL stored results for the chosen class and improve the storage for later
        use and analysis.
        '''
        self.teaching_set = teaching_set
        self.DBname = DBname

        with sqlite3.connect(DBname) as DB:
            query = "SELECT * FROM results WHERE teaching_set = ?"
            # -- Format is: aID; UPN; teaching_set; aName; qNum; pMark
            res = DB.execute(query, (teaching_set,)).fetchall()

            # -- prep question mark data for combining into the result tuples
            self.assessmentMarks = dict()
            self.assessmentIDs = set([r[0] for r in res])
            for a in self.assessmentIDs:
                query = "SELECT qNum, qMark from assessments where aID = ?"
                qScores = DB.execute(query, (a,)).fetchall()
                for q in qScores:
                    key = str(a) + '/' + str(q[0])
                    self.assessmentMarks[key] = q[1]

        # -- Improve readability for main dataset: class_results should NOT be mutated
        result = namedtuple('Result', ['UPN', 'tSet', 'aID', 'qNum', 'mark', 'total'])
        self.class_results = [result(r[1], r[2], r[0], r[4], r[5], self.assessmentMarks[str(r[0]) + '/' + str(r[4])]) for r in res]

        # -- active_results is set every time we normalise the data against a target.
        self.active_results = list()

    def normalise(self, against='class'):
        '''
        Normalise the pupil results versus:
            Their class         -- "class"
            The whole cohort    -- "cohort"
            Same estimate       -- "estimate"
            Same entry point    -- "entryPoint"
        '''
        # -- Reset the active_results list
        self.active_results = list()

        # -- each aID acts as a key to retrieve a list of question means
        detailDict = dict()

        # -- grab mean question scores for each question sat by the class
        for a in self.assessmentIDs:
            aDetails = dict()
            with sqlite3.connect(self.DBname) as DB:
                query = "select count(*) from assessments where aID = ?"
                numQs = DB.execute(query, (a,)).fetchone()[0]

            for qNum in range(1, numQs + 1):
                classMarks = [r.mark for r in self.class_results if r.aID == a and r.qNum == qNum]
                mean = sum(classMarks) / len(classMarks)
                aDetails[qNum] = mean
            detailDict[a] = aDetails

        # -- NOTE: This is where we normalise the pupil mark with respect to the mean
        result = namedtuple('NormalisedResult', ['UPN', 'tSet', 'aID', 'qNum', 'norm'])
        for r in self.class_results:
            norm = (r.mark - detailDict[r.aID][r.qNum]) / r.total
            normRes = result(r.UPN, r.tSet, r.aID, r.qNum, float("{0:.5f}".format(norm)))
            self.active_results.append(normRes)

    def select(self, mode='worst', numPerPupil=3):
        '''
        For each pupil and each assessment, identify their best/worst questions.
        Return is a dict of {aID:
                                {UPN: worst results,
                                ...},
                            ...}
        '''
        assert((mode == 'worst') or (mode == 'best'))
        # -- fetch pupil UPNs
        with sqlite3.connect(self.DBname) as DB:
            query = "SELECT UPN from cohort where teaching_set = ?"
            UPNs = DB.execute(query, (self.teaching_set,)).fetchall()

        classPerformance = dict()
        for aID in self.assessmentIDs:
            with sqlite3.connect(self.DBname) as DB:
                query = "SELECT qNum, qTitle FROM assessments where aID = ?"
                qTitles = DB.execute(query, (aID,)).fetchall()
                titleDict = dict()
                for q in qTitles:
                    titleDict[q[0]] = q[1]
            pupilPerformance = dict()
            for UPN in UPNs:
                performance = [r for r in self.active_results if r.aID == aID and r.UPN == UPN[0]]
                performance = sorted(performance, key=lambda x: x.norm)
                if mode == 'worst':
                    perf = performance[:numPerPupil]
                else:
                    perf = performance[-numPerPupil:]
                readable_results = [(titleDict[r.qNum], r.norm) for r in perf]

                with sqlite3.connect(self.DBname) as DB:
                    query = "SELECT Name FROM cohort WHERE UPN = ?"
                    name = DB.execute(query, (UPN[0],)).fetchone()[0]

                pupilPerformance[name] = readable_results
            # -- OrderedDict to maintain register order of pupils
            classPerformance[aID] = OrderedDict(sorted(pupilPerformance.items()))

        self.output = classPerformance

    def write_to_txt(self, filename="output.txt"):
        with open(filename, "w") as f:
            f.write("Here are the lowest performing topics per pupil vs the class mean.\n"
                    "Normalised performance has been calculated as:\n"
                    "  norm = (pupil score - class mean) / question total\n\n")
            for assessment in self.output:
                with sqlite3.connect(self.DBname) as DB:
                    query = "SELECT aName FROM assessments WHERE aID = ?"
                    aName = DB.execute(query, (assessment,)).fetchone()[0]
                f.write("Assessment: {}".format(aName))
                for pupil in self.output[assessment]:
                    f.write('\n ' + pupil + ':\n')
                    for Q in self.output[assessment][pupil]:
                        f.write("  {}: ({})\n".format(Q[0].strip(), Q[1]))
                f.write('\n\n')

    def write_to_xlsx(self, filename="output.xlsx"):
        # This uses openpyxl
        wb = Workbook()
        # This will create a new sheet --> ws = wb.create_sheet()
        ws = wb.active
        ws.title = "ClMATE Assessment analysis - " + self.teaching_set

        ''' This is from the data entry screen - REWRITE! '''
        # -- Set up column headings
        headings = ['UPN', 'Pupil name', 'Target']
        for n in range(NUM_QUESTIONS):
            headings.append(str(n + 1))
        headings.append('Total')
        headings.append('  %  ')
        headings.append('Grade')
        headings.append('Relative')
        for col in range(NUM_QUESTIONS + 7):
            heading = ws.cell(row=1, column=(col + 1))
            heading.value = headings[col]

        # -- Rip data
        DBname = self.session_details["DBname"]
        with sqlite3.connect(DBname) as DB:
            for r in range(self.CLASS_SIZE):
                upn_val = DB.execute("select UPN from cohort where name = ?",
                                     (self.name_list[r],)).fetchone()[0]
                upn = ws.cell(row=(r + 2), column=1)
                upn.value = upn_val
                for c in range(NUM_QUESTIONS + 5):
                    cell_contents = str(questions.item(r, c).text())
                    excel_cell = ws.cell(row=(r + 2), column=(c + 2))
                    excel_cell.value = cell_contents
                rel = str(questions.item(r, NUM_QUESTIONS + 5).text()[1:])
                excel_cell = ws.cell(row=(r + 2), column=(NUM_QUESTIONS + 7))
                excel_cell.value = rel
        DB.close()

        wb.save(title)


if __name__ == '__main__':
    y11 = ['11-PG', '11-DBY', '11-HH', '11-CCL', '11-AR', '11-AK', '11-IM', '11-MD']
    for tSet in y11:
        r = Reviewer(teaching_set=tSet, DBname="ClMATE_DB.db")
        r.normalise(against='class')
        r.select(mode='worst', numPerPupil=3)
        r.write_to_txt(tSet + " - worst 3.txt")
