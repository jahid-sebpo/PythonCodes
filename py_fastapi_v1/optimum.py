OPTIMUMBOARD = """

    <main class="max-w-5xl w-full mx-auto grid grid-cols-1 md:grid-cols-12 gap-6 flex-1">
        
        <!-- Controls & Upload Form Section -->
        <div class="md:col-span-5 flex flex-col gap-5">
            <form id="uploadForm" class="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-5 shadow-xl flex flex-col gap-4">
                
                <div>
                    <label class="block text-sm font-medium text-slate-300 mb-2">Excel File (.xlsx, .xls)</label>
                    <div id="dropZone" class="border-2 border-dashed border-slate-600 hover:border-indigo-500 bg-slate-900/50 rounded-xl p-6 text-center cursor-pointer transition-all duration-200">
                        <svg class="mx-auto h-10 w-10 text-indigo-400 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 0115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                        </svg>
                        <p id="fileNameDisplay" class="text-xs text-slate-300 font-medium">Click to browse or drag & drop file here</p>
                        <p class="text-[11px] text-slate-500 mt-1">Supports matrixfile.xlsx</p>
                        <input type="file" id="fileInput" name="file" accept=".xlsx, .xls" class="hidden" required>
                    </div>
                </div>

                <div>
                    <label for="sheetName" class="block text-sm font-medium text-slate-300 mb-1">Sheet / Tab Name</label>
                    <input type="text" id="sheetName" name="sheet_name" value="FT Matrix Output" 
                        class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3.5 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500 transition-colors"
                        placeholder="e.g. FT Matrix Output">
                </div>

                <div>
                    <label for="orient" class="block text-sm font-medium text-slate-300 mb-1">Output Structure</label>
                    <select id="orient" name="orient" 
                        class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3.5 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500 transition-colors">
                        <option value="records">Array of Objects (JSON Records)</option>
                        <!-- <option value="list">2D Matrix Array (Including Header)</option> -->
                    </select>
                </div>

                <!-- Submit Button -->
                <button type="submit" id="submitBtn" 
                    class="mt-2 w-full bg-indigo-600 hover:bg-indigo-500 active:scale-[0.98] text-white font-medium py-2.5 px-4 rounded-xl shadow-lg shadow-indigo-600/25 transition-all flex justify-center items-center gap-2">
                    <svg id="btnSpinner" class="hidden animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span id="btnText">Generate Versions</span>
                </button>
            </form>

            <!-- Status Banner -->
            <div id="toastMessage" class="hidden p-4 rounded-xl border text-xs font-medium transition-all"></div>
        </div>
    </main>

"""
