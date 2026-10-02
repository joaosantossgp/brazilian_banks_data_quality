/* Hard raw-body and execution bounds; partial evidence is never accepted. */
class Budget {
  constructor(maxBytes=80*1024*1024,maxMs=480000,start=Date.now()) {
    this.maxBytes=maxBytes;this.deadline=start+maxMs;this.bytes=0;this.exceeded=false;
  }
  checkTime(now=Date.now()) {if(now>=this.deadline)throw Error('Execution time budget exceeded');}
  checkSpace(available,reserve=150*1024*1024) {if(available<reserve)throw Error('Disk reserve unavailable');}
  take(size,now=Date.now()) {
    this.checkTime(now);
    const accepted=Math.min(size,this.maxBytes-this.bytes);
    this.bytes+=accepted;
    if(accepted<size)this.exceeded=true;
    return accepted;
  }
}
module.exports={Budget};
