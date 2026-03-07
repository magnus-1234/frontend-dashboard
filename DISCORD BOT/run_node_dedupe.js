const dns = require('dns');
dns.setServers(['8.8.8.8', '8.8.4.4']); // Force Google DNS to bypass ISP SRV blocks

const { MongoClient } = require('mongodb');

const MONGO_URI = 'mongodb+srv://iammagnusx1_db_user:zYFHUOjjXhfGLpMs@reminderbot.r6hso.mongodb.net/?retryWrites=true&w=majority&appName=WOSBOT';
const MONGO_WOS_URI = 'mongodb+srv://admin:Magnus123@cluster0.p8vbe.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0';

async function run() {
    console.log(">>> [START] Node Dedupe Started");
    const client_main = new MongoClient(MONGO_URI, { serverSelectionTimeoutMS: 5000 });
    let client_wos = null;

    try {
        console.log(">>> [DB] Connecting to Primary...");
        await client_main.connect();
        const db_main = client_main.db('reminderbot');
        console.log(">>> [DB] Connected.");

        try {
            console.log(">>> [DB] Connecting to Secondary WOS...");
            client_wos = new MongoClient(MONGO_WOS_URI, { serverSelectionTimeoutMS: 5000 });
            await client_wos.connect();
            console.log(">>> [DB] Secondary connected.");
        } catch (e) {
            console.log(">>> [DB] Secondary WOS failed, continuing with primary.");
        }

        const dbs = [db_main];
        if (client_wos) dbs.push(client_wos.db('reminderbot'));

        console.log(">>> [QUERY] Looking for ICE alliance...");
        const alliance = await db_main.collection('alliance__alliance_list').findOne({ name: 'ICE' });
        if (!alliance) {
            console.log(">>> [ERROR] ICE alliance not found.");
            process.exit(1);
        }

        const guild_id = alliance.discord_server_id;
        console.log(`>>> [VARS] Found ICE Guild ID: ${guild_id}`);
        const search_gid = [Number(guild_id), String(guild_id)];

        const unique_members = new Map();
        const docs_to_delete = [];
        let total_found = 0;

        for (let i = 0; i < dbs.length; i++) {
            const db = dbs[i];
            console.log(`>>> [ITER] Querying DB #${i}...`);
            const coll = db.collection('auto_redeem_members');
            const docs = await coll.find({ guild_id: { $in: search_gid } }).toArray();
            
            total_found += docs.length;
            console.log(`>>> [ITER] Found ${docs.length} docs in this cluster.`);

            for (const doc of docs) {
                if (doc.fid && String(doc.fid).toLowerCase() !== 'none') {
                    const fid = String(doc.fid).trim();
                    if (!unique_members.has(fid)) {
                        unique_members.set(fid, doc);
                    } else {
                        docs_to_delete.push({ db_idx: i, id: doc._id });
                    }
                } else if (Array.isArray(doc.members)) {
                    for (const m of doc.members) {
                        if (m.fid && String(m.fid).toLowerCase() !== 'none') {
                            const mfid = String(m.fid).trim();
                            if (!unique_members.has(mfid)) {
                                unique_members.set(mfid, {
                                    guild_id: Number(guild_id),
                                    fid: mfid,
                                    nickname: m.nickname || 'Unknown',
                                    furnace_lv: Number(m.furnace_lv) || 0,
                                    avatar_image: m.avatar_image || '',
                                    added_by: Number(m.added_by) || 0,
                                    added_at: m.added_at || new Date().toISOString()
                                });
                            }
                        }
                    }
                    docs_to_delete.push({ db_idx: i, id: doc._id });
                }
            }
        }

        console.log(`>>> [RESULTS] Searched ${total_found} entries. Identified ${unique_members.size} core members.`);
        console.log(`>>> [RESULTS] Marked ${docs_to_delete.length} duplicate/legacy documents for deletion.`);

        if (docs_to_delete.length > 0) {
            console.log(">>> [ACTION] Deleting duplicates...");
            let deleted = 0;
            for (const item of docs_to_delete) {
                const coll = dbs[item.db_idx].collection('auto_redeem_members');
                const res = await coll.deleteOne({ _id: item.id });
                deleted += res.deletedCount;
            }
            console.log(`>>> [ACTION] Successfully deleted ${deleted} duplicates.`);

            console.log(">>> [ACTION] Upserting core members into primary DB...");
            const main_coll = db_main.collection('auto_redeem_members');
            let upserted = 0;
            for (const [fid, data] of unique_members.entries()) {
                delete data._id; // Remove _id for clean upsert
                const res = await main_coll.updateOne(
                    { guild_id: Number(guild_id), fid: String(fid) },
                    { $set: data },
                    { upsert: true }
                );
                if (res.upsertedCount > 0 || res.modifiedCount > 0) upserted++;
            }
            console.log(`>>> [ACTION] Successfully wrote ${upserted} core ICE members.`);
        }

        console.log(">>> [DONE] ICE Deduplication complete.");

    } catch (e) {
        console.error(">>> [CRASH] Fatal exception:", e);
    } finally {
        await client_main.close();
        if (client_wos) await client_wos.close();
        console.log(">>> [EXIT] Connections closed.");
    }
}

run();
