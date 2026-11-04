// Inert stand-in for a poisoned dev container setup step.
//
// A postCreateCommand runs on every machine that opens the repository in
// a dev container, before anyone reviews what it does. This one reads
// nothing, sends nothing, and exits.
process.exit(0);
