//
// microtome-test

package microtome.test {

public function assertThrows (f :Function, failureMessage :String="") :void {
    try {
        f();
    } catch (e :Error) {
        return;
    }
    throw new Error(failureMessage);
}

}
